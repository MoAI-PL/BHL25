#!/usr/bin/env python3
"""
CodeCarbon Estimation Bridge
Estimates CO2 emissions for Python code WITHOUT executing it
Uses static analysis and heuristics
"""
import sys
import json
import ast
import re

# Estimated CO2 per operation (in grams) - based on typical CPU energy consumption
CO2_ESTIMATES = {
    'loop_iteration': 0.000001,  # 1 microgram per iteration
    'file_operation': 0.00001,   # 10 micrograms per file op
    'function_call': 0.0000005,  # 0.5 micrograms per call
    'import': 0.00002,           # 20 micrograms per import
    'list_comprehension': 0.0000005,  # More efficient than loops
}

def estimate_co2(code):
    """
    Estimates CO2 emissions based on code structure
    Returns estimated CO2 in grams and breakdown
    """
    total_co2 = 0.0
    breakdown = {}
    
    lines = code.split('\n')
    
    # Count different operations
    loop_count = 0
    nested_loops = 0
    file_ops = 0
    imports = 0
    function_calls = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Count loops
        if re.match(r'for\s+\w+\s+in\s+range\s*\(', line_stripped):
            loop_count += 1
            # Try to extract range size
            match = re.search(r'range\s*\(\s*(\d+)\s*\)', line)
            if match:
                iterations = int(match.group(1))
                total_co2 += iterations * CO2_ESTIMATES['loop_iteration']
                breakdown[f'loop_line_{i+1}'] = iterations * CO2_ESTIMATES['loop_iteration']
            else:
                # Default estimate
                total_co2 += 1000 * CO2_ESTIMATES['loop_iteration']
                breakdown[f'loop_line_{i+1}'] = 1000 * CO2_ESTIMATES['loop_iteration']
        
        # Count file operations
        if 'open(' in line:
            file_ops += 1
            total_co2 += CO2_ESTIMATES['file_operation']
        
        # Count imports
        if line_stripped.startswith('import ') or line_stripped.startswith('from '):
            imports += 1
            total_co2 += CO2_ESTIMATES['import']
        
        # Count function calls (rough estimate)
        function_calls += len(re.findall(r'\w+\s*\(', line))
    
    total_co2 += function_calls * CO2_ESTIMATES['function_call']
    
    # Calculate energy (1g CO2 ≈ 0.002 kWh for typical energy mix)
    energy_kwh = total_co2 * 0.002
    
    result = {
        'estimated_co2_grams': round(total_co2, 6),
        'estimated_co2_kg': round(total_co2 / 1000, 9),
        'estimated_energy_kwh': round(energy_kwh, 6),
        'operations': {
            'loops': loop_count,
            'file_operations': file_ops,
            'imports': imports,
            'function_calls': function_calls
        },
        'breakdown': breakdown,
        'note': 'This is a static estimate. Actual emissions depend on hardware and runtime.'
    }
    
    return result

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        # Read from stdin
        code = sys.stdin.read()
    
    result = estimate_co2(code)
    print(json.dumps(result, indent=2))

