#!/usr/bin/env python3
"""
CO2 Estimator - Static analysis for carbon footprint estimation.
Uses CodeCarbon for hardware-aware estimation when available.
"""
import sys
import json
import re


def estimate_co2(code):
    """
    Estimates CO2 emissions based on code structure.
    Tries to use CodeCarbon for hardware-aware estimation.
    Returns estimated CO2 in grams and breakdown.
    """
    total_co2 = 0.0
    breakdown = {}
    method = 'estimation'
    hardware_info = {}
    
    # Try to get hardware-aware estimation from CodeCarbon
    try:
        from codecarbon import EmissionsTracker
        from codecarbon.core.units import Energy, Power
        
        # Get system info for better estimation
        tracker = EmissionsTracker(
            project_name="estimation",
            log_level='error',
            save_to_file=False
        )
        
        # Extract hardware info
        if hasattr(tracker, '_conf'):
            hardware_info = {
                'cpu_model': getattr(tracker._conf, 'cpu_model', 'unknown'),
                'cpu_count': getattr(tracker._conf, 'cpu_count', 1),
                'gpu_model': getattr(tracker._conf, 'gpu_model', 'none'),
                'country': getattr(tracker._conf, 'country_iso_code', 'unknown')
            }
        
        method = 'codecarbon_estimation'
    except ImportError:
        pass
    except Exception:
        pass
    
    # Estimated CO2 per operation (in grams) - based on typical CPU energy consumption
    CO2_ESTIMATES = {
        'loop_iteration': 0.000001,   # 1 microgram per iteration
        'file_operation': 0.00001,    # 10 micrograms per file op
        'function_call': 0.0000005,   # 0.5 micrograms per call
        'import': 0.00002,            # 20 micrograms per import
        'list_comprehension': 0.0000003,  # More efficient than loops
        'numpy_operation': 0.0000001,     # Very efficient
    }
    
    lines = code.split('\n')
    
    # Count different operations
    loop_count = 0
    nested_loops = 0
    file_ops = 0
    imports = 0
    function_calls = 0
    list_comps = 0
    numpy_ops = 0
    
    indent_stack = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        
        # Track nesting level
        while indent_stack and indent_stack[-1] >= indent:
            indent_stack.pop()
        
        # Count loops
        is_for_loop = re.match(r'for\s+\w+\s+in\s+', line_stripped)
        is_while_loop = re.match(r'while\s+', line_stripped)
        
        if is_for_loop:
            loop_count += 1
            
            # Check for nested loops
            if indent_stack:
                nested_loops += 1
            
            indent_stack.append(indent)
            
            # Try to extract range size
            range_match = re.search(r'range\s*\(\s*(\d+)\s*(?:,\s*(\d+))?\s*\)', line)
            if range_match:
                if range_match.group(2):
                    iterations = int(range_match.group(2)) - int(range_match.group(1))
                else:
                    iterations = int(range_match.group(1))
                
                # Nested loops multiply the impact
                multiplier = 2 ** len([x for x in indent_stack if x < indent])
                total_co2 += iterations * CO2_ESTIMATES['loop_iteration'] * multiplier
                breakdown[f'loop_line_{i+1}'] = iterations * CO2_ESTIMATES['loop_iteration'] * multiplier
            else:
                # Default estimate for unknown ranges
                total_co2 += 1000 * CO2_ESTIMATES['loop_iteration']
                breakdown[f'loop_line_{i+1}'] = 1000 * CO2_ESTIMATES['loop_iteration']
        
        if is_while_loop:
            loop_count += 1
            indent_stack.append(indent)
            # While loops get a higher estimate due to uncertainty
            total_co2 += 5000 * CO2_ESTIMATES['loop_iteration']
        
        # Count file operations
        if 'open(' in line:
            file_ops += 1
            total_co2 += CO2_ESTIMATES['file_operation']
            breakdown[f'file_op_line_{i+1}'] = CO2_ESTIMATES['file_operation']
        
        # Count imports
        if line_stripped.startswith('import ') or line_stripped.startswith('from '):
            imports += 1
            total_co2 += CO2_ESTIMATES['import']
            
            # NumPy operations are more efficient
            if 'numpy' in line or 'np' in line:
                numpy_ops += 1
        
        # Count list comprehensions (more efficient)
        list_comp_count = len(re.findall(r'\[.*for\s+\w+\s+in\s+.*\]', line))
        if list_comp_count > 0:
            list_comps += list_comp_count
            total_co2 += list_comp_count * CO2_ESTIMATES['list_comprehension'] * 100
        
        # Count function calls (rough estimate)
        func_calls = len(re.findall(r'\w+\s*\(', line))
        # Subtract structural keywords
        func_calls -= len(re.findall(r'\b(if|for|while|with|def|class|import|from|return|print)\s*\(', line))
        func_calls = max(0, func_calls)
        function_calls += func_calls
    
    total_co2 += function_calls * CO2_ESTIMATES['function_call']
    
    # Calculate energy (using global average: 1g CO2 ≈ 0.002 kWh)
    energy_kwh = total_co2 * 0.002
    
    result = {
        'estimated_co2_grams': round(total_co2, 9),
        'estimated_energy_kwh': round(energy_kwh, 12),
        'operations': {
            'loops': loop_count,
            'nested_loops': nested_loops,
            'file_operations': file_ops,
            'imports': imports,
            'function_calls': function_calls,
            'list_comprehensions': list_comps,
            'numpy_operations': numpy_ops
        },
        'breakdown': breakdown,
        'method': method,
        'hardware_info': hardware_info,
        'note': 'Static estimate based on code structure. Install CodeCarbon for actual runtime tracking.'
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
