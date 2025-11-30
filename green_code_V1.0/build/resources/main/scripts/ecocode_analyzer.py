#!/usr/bin/env python3
"""
Eco Code Analyzer Integration Script
Uses the eco-code-analyzer library for static analysis of Python code efficiency.
Falls back to built-in analysis if the library is not installed.
"""
import sys
import json
import re
import ast


def analyze_with_ecocode(code):
    """
    Analyze code using the eco-code-analyzer library.
    Returns list of issues with line numbers, severity, and recommendations.
    """
    issues = []
    
    try:
        from eco_code_analyzer import analyze_code as eco_analyze, get_eco_score
        
        # Use the actual eco-code-analyzer library
        analysis_result = eco_analyze(code)
        
        # Get eco score if available
        try:
            eco_score = get_eco_score(analysis_result)
        except:
            eco_score = None
        
        # Convert eco-code-analyzer output to our format
        if isinstance(analysis_result, dict):
            if 'issues' in analysis_result:
                for issue in analysis_result['issues']:
                    issues.append({
                        'line': issue.get('line', 1),
                        'severity': issue.get('severity', 'warning'),
                        'type': issue.get('type', 'efficiency'),
                        'message': issue.get('message', 'Code efficiency issue'),
                        'suggestion': issue.get('suggestion', ''),
                        'co2_impact': issue.get('impact', 'medium'),
                        'source': 'eco-code-analyzer'
                    })
            
            # Add eco score to results
            if eco_score is not None:
                issues.insert(0, {
                    'line': 0,
                    'severity': 'info',
                    'type': 'eco_score',
                    'message': f'Eco Score: {eco_score}',
                    'co2_impact': 'info',
                    'source': 'eco-code-analyzer'
                })
        elif isinstance(analysis_result, list):
            for item in analysis_result:
                if isinstance(item, dict):
                    issues.append({
                        'line': item.get('line', 1),
                        'severity': item.get('severity', 'warning'),
                        'type': item.get('type', 'efficiency'),
                        'message': item.get('message', str(item)),
                        'co2_impact': item.get('impact', 'medium'),
                        'source': 'eco-code-analyzer'
                    })
                    
    except ImportError:
        # eco-code-analyzer not installed, use built-in analysis
        issues = builtin_eco_analysis(code)
        for issue in issues:
            issue['source'] = 'builtin-fallback'
            issue['note'] = 'eco-code-analyzer not installed. Install with: pip install eco-code-analyzer'
            
    except Exception as e:
        # Error using library, fall back to built-in
        issues = builtin_eco_analysis(code)
        for issue in issues:
            issue['source'] = 'builtin-fallback'
            issue['error'] = str(e)
    
    return issues


def builtin_eco_analysis(code):
    """
    Built-in eco code analysis when external library is not available.
    Checks for common energy-inefficient patterns.
    """
    issues = []
    lines = code.split('\n')
    
    # Track indentation levels for nested loop detection
    loop_stack = []
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        
        # Skip empty lines and comments
        if not line_stripped or line_stripped.startswith('#'):
            continue
        
        # Update loop stack based on indentation
        while loop_stack and loop_stack[-1][1] >= indent:
            loop_stack.pop()
        
        # Check 1: Inefficient loops with range
        if re.match(r'for\s+\w+\s+in\s+range\s*\(', line_stripped):
            # Check for large ranges
            match = re.search(r'range\s*\(\s*(\d+)\s*\)', line)
            if match:
                iterations = int(match.group(1))
                if iterations > 10000:
                    issues.append({
                        'line': i,
                        'severity': 'warning',
                        'type': 'large_loop',
                        'message': f'Large loop with {iterations} iterations. Consider vectorization with NumPy.',
                        'suggestion': 'Use numpy.arange() or numpy.vectorize() for better performance.',
                        'co2_impact': 'high'
                    })
                elif iterations > 1000:
                    issues.append({
                        'line': i,
                        'severity': 'info',
                        'type': 'medium_loop',
                        'message': f'Loop with {iterations} iterations. Consider using list comprehension.',
                        'suggestion': 'List comprehensions are often more efficient than explicit loops.',
                        'co2_impact': 'medium'
                    })
            
            # Check for nested loops
            if loop_stack:
                parent_line = loop_stack[-1][0]
                issues.append({
                    'line': i,
                    'severity': 'error',
                    'type': 'nested_loop',
                    'message': f'Nested loop detected (outer loop at line {parent_line}). High CPU/energy usage.',
                    'suggestion': 'Consider using NumPy operations, pandas, or itertools.product().',
                    'co2_impact': 'high'
                })
            
            loop_stack.append((i, indent))
        
        # Check 2: While loops (potentially infinite)
        elif re.match(r'while\s+', line_stripped):
            if 'True' in line_stripped or 'true' in line_stripped:
                issues.append({
                    'line': i,
                    'severity': 'warning',
                    'type': 'infinite_loop_risk',
                    'message': 'Potentially infinite while loop detected.',
                    'suggestion': 'Ensure proper break conditions to avoid wasted CPU cycles.',
                    'co2_impact': 'high'
                })
            loop_stack.append((i, indent))
        
        # Check 3: File operations without context manager
        if re.search(r'[=]\s*open\s*\(', line) and 'with ' not in line:
            issues.append({
                'line': i,
                'severity': 'warning',
                'type': 'resource_leak',
                'message': 'File opened without context manager.',
                'suggestion': 'Use "with open(...) as f:" to ensure proper resource cleanup.',
                'co2_impact': 'low'
            })
        
        # Check 4: Wildcard imports
        if re.match(r'from\s+\w+.*import\s+\*', line_stripped):
            issues.append({
                'line': i,
                'severity': 'warning',
                'type': 'wildcard_import',
                'message': 'Wildcard import loads unnecessary modules into memory.',
                'suggestion': 'Import only the specific functions/classes you need.',
                'co2_impact': 'low'
            })
        
        # Check 5: String concatenation in loops
        if '+=' in line and ('str' in line or '"' in line or "'" in line):
            # Check if we're inside a loop
            if loop_stack:
                issues.append({
                    'line': i,
                    'severity': 'warning',
                    'type': 'string_concat_loop',
                    'message': 'String concatenation inside loop is inefficient.',
                    'suggestion': 'Use list.append() and "".join() for better performance.',
                    'co2_impact': 'medium'
                })
        
        # Check 6: Global variables usage
        if line_stripped.startswith('global '):
            issues.append({
                'line': i,
                'severity': 'info',
                'type': 'global_variable',
                'message': 'Global variable usage can impact performance.',
                'suggestion': 'Consider passing variables as function parameters.',
                'co2_impact': 'low'
            })
        
        # Check 7: Repeated function calls that could be cached
        if re.search(r'(\w+\([^)]*\)).*\1', line):
            issues.append({
                'line': i,
                'severity': 'info',
                'type': 'repeated_call',
                'message': 'Repeated function call on same line.',
                'suggestion': 'Consider caching the result in a variable.',
                'co2_impact': 'low'
            })
        
        # Check 8: Sleep statements (wasting time/energy)
        if 'time.sleep(' in line or 'sleep(' in line:
            match = re.search(r'sleep\s*\(\s*(\d+(?:\.\d+)?)\s*\)', line)
            if match:
                sleep_time = float(match.group(1))
                if sleep_time > 1:
                    issues.append({
                        'line': i,
                        'severity': 'info',
                        'type': 'long_sleep',
                        'message': f'Long sleep of {sleep_time}s detected.',
                        'suggestion': 'Consider if this delay is necessary or can be reduced.',
                        'co2_impact': 'low'
                    })
        
        # Check 9: Print statements in loops (I/O is expensive)
        if 'print(' in line and loop_stack:
            issues.append({
                'line': i,
                'severity': 'info',
                'type': 'print_in_loop',
                'message': 'Print statement inside loop causes repeated I/O.',
                'suggestion': 'Collect output and print once after the loop.',
                'co2_impact': 'medium'
            })
        
        # Check 10: Inefficient list operations
        if '.append(' in line and 'for ' in line:
            issues.append({
                'line': i,
                'severity': 'info',
                'type': 'list_append_pattern',
                'message': 'List building pattern detected.',
                'suggestion': 'Consider using list comprehension for better performance.',
                'co2_impact': 'low'
            })
        
        # Check 11: Reading entire file into memory
        if '.read()' in line or '.readlines()' in line:
            issues.append({
                'line': i,
                'severity': 'info',
                'type': 'full_file_read',
                'message': 'Reading entire file into memory.',
                'suggestion': 'For large files, iterate line by line: for line in file:',
                'co2_impact': 'medium'
            })
        
        # Check 12: Recursive functions (potential stack overflow)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name) and child.func.id == func_name:
                                issues.append({
                                    'line': node.lineno,
                                    'severity': 'info',
                                    'type': 'recursion',
                                    'message': f'Recursive function "{func_name}" detected.',
                                    'suggestion': 'Consider iterative approach or add memoization with @functools.lru_cache.',
                                    'co2_impact': 'medium'
                                })
                                break
        except:
            pass
    
    return issues


def get_eco_score(issues):
    """
    Calculate an eco score based on the issues found.
    Score from 0-100, where 100 is best (no issues).
    """
    if not issues:
        return 100
    
    score = 100
    
    for issue in issues:
        severity = issue.get('severity', 'info')
        impact = issue.get('co2_impact', 'low')
        
        # Deduct points based on severity and impact
        if severity == 'error':
            score -= 15
        elif severity == 'warning':
            score -= 8
        else:
            score -= 3
        
        # Additional deduction for high impact
        if impact == 'high':
            score -= 5
        elif impact == 'medium':
            score -= 2
    
    return max(0, score)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        # Read from stdin
        code = sys.stdin.read()
    
    issues = analyze_with_ecocode(code)
    eco_score = get_eco_score(issues)
    
    result = {
        'eco_score': eco_score,
        'issues': issues,
        'total_issues': len(issues),
        'summary': {
            'errors': len([i for i in issues if i.get('severity') == 'error']),
            'warnings': len([i for i in issues if i.get('severity') == 'warning']),
            'info': len([i for i in issues if i.get('severity') == 'info'])
        }
    }
    
    print(json.dumps(result, indent=2))

