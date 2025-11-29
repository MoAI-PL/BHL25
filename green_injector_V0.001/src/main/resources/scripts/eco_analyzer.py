#!/usr/bin/env python3
"""
Eco Code Analyzer Bridge
Analyzes Python code and returns issues in JSON format
"""
import sys
import json
import ast
import re

def analyze_code(code):
    """
    Analyzes Python code for energy efficiency issues
    Returns list of issues with line numbers and severity
    """
    issues = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Check 1: Inefficient loops
        if re.match(r'for\s+\w+\s+in\s+range\s*\(', line_stripped):
            if 'enumerate' not in line:
                issues.append({
                    'line': i,
                    'severity': 'warning',
                    'type': 'inefficient_loop',
                    'message': 'Inefficient loop detected. Consider using NumPy or list comprehension.',
                    'co2_impact': 'medium'
                })
        
        # Check 2: File operations without context manager
        if 'open(' in line and 'with ' not in line and 'def ' not in line:
            if re.search(r'=\s*open\s*\(', line):
                issues.append({
                    'line': i,
                    'severity': 'warning',
                    'type': 'resource_leak',
                    'message': 'File opened without context manager. Use "with open(...)"',
                    'co2_impact': 'low'
                })
        
        # Check 3: Wildcard imports
        if re.match(r'from\s+\w+.*import\s+\*', line_stripped):
            issues.append({
                'line': i,
                'severity': 'warning',
                'type': 'wildcard_import',
                'message': 'Wildcard import wastes memory. Import specific items.',
                'co2_impact': 'low'
            })
        
        # Check 4: Nested loops (high CPU usage)
        if 'for ' in line:
            indent = len(line) - len(line.lstrip())
            # Check if there's another for loop nearby with less indent (parent loop)
            for j in range(max(0, i-5), i):
                if j < len(lines) and 'for ' in lines[j]:
                    parent_indent = len(lines[j]) - len(lines[j].lstrip())
                    if parent_indent < indent:
                        issues.append({
                            'line': i,
                            'severity': 'error',
                            'type': 'nested_loop',
                            'message': 'Nested loops are extremely CPU-intensive. Consider vectorization.',
                            'co2_impact': 'high'
                        })
                        break
    
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

