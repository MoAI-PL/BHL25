#!/usr/bin/env python3
"""
Eco Code Analyzer Bridge - Wrapper for eco-code-analyzer library.
Analyzes Python code and returns issues in JSON format.
Falls back to built-in analysis if library is not available.
"""
import sys
import json
import re


def analyze_code(code):
    """
    Analyzes Python code for energy efficiency issues.
    Tries to use eco-code-analyzer library first, falls back to built-in analysis.
    Returns list of issues with line numbers and severity.
    """
    # Try using the eco-code-analyzer library first
    try:
        from eco_code_analyzer import analyze_code as eco_analyze
        
        result = eco_analyze(code)
        
        # Convert library output to our format
        if isinstance(result, dict) and 'issues' in result:
            issues = []
            for issue in result['issues']:
                issues.append({
                    'line': issue.get('line', 1),
                    'severity': issue.get('severity', 'warning'),
                    'type': issue.get('type', 'efficiency'),
                    'message': issue.get('message', 'Efficiency issue detected'),
                    'co2_impact': issue.get('impact', 'medium'),
                    'source': 'eco-code-analyzer'
                })
            return issues
        elif isinstance(result, list):
            issues = []
            for item in result:
                if isinstance(item, dict):
                    issues.append({
                        'line': item.get('line', 1),
                        'severity': item.get('severity', 'warning'),
                        'type': item.get('type', 'efficiency'),
                        'message': item.get('message', str(item)),
                        'co2_impact': item.get('impact', 'medium'),
                        'source': 'eco-code-analyzer'
                    })
            return issues
            
    except ImportError:
        pass  # Fall through to built-in analysis
    except Exception as e:
        pass  # Fall through to built-in analysis
    
    # Built-in fallback analysis
    return builtin_analysis(code)


def builtin_analysis(code):
    """
    Built-in code analysis for energy efficiency issues.
    Used when eco-code-analyzer library is not available.
    """
    issues = []
    lines = code.split('\n')
    
    # Track loop nesting
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
        
        # Check 1: Inefficient loops
        if re.match(r'for\s+\w+\s+in\s+range\s*\(', line_stripped):
            if 'enumerate' not in line:
                # Check for nested loops
                if loop_stack:
                    issues.append({
                        'line': i,
                        'severity': 'error',
                        'type': 'nested_loop',
                        'message': 'Nested loops are extremely CPU-intensive. Consider vectorization.',
                        'co2_impact': 'high',
                        'source': 'builtin'
                    })
                else:
                    issues.append({
                        'line': i,
                        'severity': 'warning',
                        'type': 'inefficient_loop',
                        'message': 'Inefficient loop detected. Consider using NumPy or list comprehension.',
                        'co2_impact': 'medium',
                        'source': 'builtin'
                    })
            loop_stack.append((i, indent))
        
        # Also track while loops
        if re.match(r'while\s+', line_stripped):
            loop_stack.append((i, indent))
        
        # Check 2: File operations without context manager
        if 'open(' in line and 'with ' not in line and 'def ' not in line:
            if re.search(r'=\s*open\s*\(', line):
                issues.append({
                    'line': i,
                    'severity': 'warning',
                    'type': 'resource_leak',
                    'message': 'File opened without context manager. Use "with open(...)"',
                    'co2_impact': 'low',
                    'source': 'builtin'
                })
        
        # Check 3: Wildcard imports
        if re.match(r'from\s+\w+.*import\s+\*', line_stripped):
            issues.append({
                'line': i,
                'severity': 'warning',
                'type': 'wildcard_import',
                'message': 'Wildcard import wastes memory. Import specific items.',
                'co2_impact': 'low',
                'source': 'builtin'
            })
        
        # Check 4: Print in loops
        if 'print(' in line and loop_stack:
            issues.append({
                'line': i,
                'severity': 'info',
                'type': 'print_in_loop',
                'message': 'Print statement inside loop causes repeated I/O operations.',
                'co2_impact': 'medium',
                'source': 'builtin'
            })
        
        # Check 5: String concatenation in loops
        if '+=' in line and loop_stack:
            if '"' in line or "'" in line or 'str' in line:
                issues.append({
                    'line': i,
                    'severity': 'warning',
                    'type': 'string_concat_loop',
                    'message': 'String concatenation in loop is inefficient. Use list.append() and join().',
                    'co2_impact': 'medium',
                    'source': 'builtin'
                })
        
        # Check 6: Reading entire file into memory
        if '.read()' in line or '.readlines()' in line:
            issues.append({
                'line': i,
                'severity': 'info',
                'type': 'full_file_read',
                'message': 'Reading entire file into memory. For large files, iterate line by line.',
                'co2_impact': 'medium',
                'source': 'builtin'
            })
    
    return issues


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        # Read from stdin
        code = sys.stdin.read()
    
    issues = analyze_code(code)
    print(json.dumps(issues, indent=2))
