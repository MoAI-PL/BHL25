#!/usr/bin/env python3
"""
CodeCarbon Integration Script
Tracks actual carbon emissions during Python code execution using the CodeCarbon library.
"""
import sys
import json
import os
import tempfile
import traceback

def run_with_codecarbon(code, timeout=60):
    """
    Execute Python code and track actual carbon emissions using CodeCarbon.
    Returns emissions data in JSON format.
    """
    result = {
        'success': False,
        'emissions_grams': 0.0,
        'energy_kwh': 0.0,
        'duration_seconds': 0.0,
        'cpu_power_watts': 0.0,
        'gpu_power_watts': 0.0,
        'ram_power_watts': 0.0,
        'country_iso_code': 'unknown',
        'region': 'unknown',
        'execution_output': '',
        'error': None,
        'method': 'codecarbon'
    }
    
    try:
        from codecarbon import EmissionsTracker
        
        # Create a temporary file to save emissions data
        emissions_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        emissions_file.close()
        
        # Create tracker with output file
        tracker = EmissionsTracker(
            project_name="green_coding_assistant",
            output_dir=os.path.dirname(emissions_file.name),
            output_file=os.path.basename(emissions_file.name),
            log_level='error',  # Suppress verbose logging
            save_to_file=True
        )
        
        # Capture stdout/stderr
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Start tracking
        tracker.start()
        
        try:
            # Execute the code
            exec_globals = {'__name__': '__main__', '__file__': '<string>'}
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, exec_globals)
            
            result['success'] = True
            result['execution_output'] = stdout_capture.getvalue()
            if stderr_capture.getvalue():
                result['execution_output'] += '\n[stderr]:\n' + stderr_capture.getvalue()
                
        except Exception as e:
            result['error'] = f"Execution error: {str(e)}"
            result['execution_output'] = traceback.format_exc()
        
        # Stop tracking and get emissions
        emissions = tracker.stop()
        
        if emissions is not None:
            # CodeCarbon returns emissions in kg, convert to grams
            result['emissions_grams'] = round(emissions * 1000, 9)
            result['energy_kwh'] = round(tracker._total_energy.kWh if hasattr(tracker, '_total_energy') else 0, 9)
            result['duration_seconds'] = round(tracker._duration if hasattr(tracker, '_duration') else 0, 3)
            result['cpu_power_watts'] = round(tracker._cpu_power.W if hasattr(tracker, '_cpu_power') else 0, 3)
            result['gpu_power_watts'] = round(tracker._gpu_power.W if hasattr(tracker, '_gpu_power') else 0, 3)
            result['ram_power_watts'] = round(tracker._ram_power.W if hasattr(tracker, '_ram_power') else 0, 3)
            result['country_iso_code'] = getattr(tracker, '_country_iso_code', 'unknown')
            result['region'] = getattr(tracker, '_region', 'unknown')
        
        # Cleanup
        try:
            os.unlink(emissions_file.name)
        except:
            pass
            
    except ImportError:
        result['error'] = "CodeCarbon not installed. Install with: pip install codecarbon"
        result['method'] = 'fallback'
        # Fall back to estimation
        result = estimate_emissions_fallback(code, result)
        
    except Exception as e:
        result['error'] = f"CodeCarbon error: {str(e)}"
        result['method'] = 'fallback'
        result = estimate_emissions_fallback(code, result)
    
    return result


def estimate_emissions_fallback(code, result=None):
    """
    Fallback estimation when CodeCarbon is not available.
    Uses static analysis heuristics.
    """
    if result is None:
        result = {
            'success': True,
            'emissions_grams': 0.0,
            'energy_kwh': 0.0,
            'duration_seconds': 0.0,
            'method': 'estimation'
        }
    
    import re
    
    # Estimated CO2 per operation (in grams)
    CO2_ESTIMATES = {
        'loop_iteration': 0.000001,
        'file_operation': 0.00001,
        'function_call': 0.0000005,
        'import': 0.00002,
    }
    
    lines = code.split('\n')
    total_co2 = 0.0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Count loops with range
        if re.match(r'for\s+\w+\s+in\s+range\s*\(', line_stripped):
            match = re.search(r'range\s*\(\s*(\d+)\s*\)', line)
            if match:
                iterations = int(match.group(1))
                total_co2 += iterations * CO2_ESTIMATES['loop_iteration']
            else:
                total_co2 += 1000 * CO2_ESTIMATES['loop_iteration']
        
        # File operations
        if 'open(' in line:
            total_co2 += CO2_ESTIMATES['file_operation']
        
        # Imports
        if line_stripped.startswith('import ') or line_stripped.startswith('from '):
            total_co2 += CO2_ESTIMATES['import']
        
        # Function calls
        total_co2 += len(re.findall(r'\w+\s*\(', line)) * CO2_ESTIMATES['function_call']
    
    result['emissions_grams'] = round(total_co2, 9)
    result['energy_kwh'] = round(total_co2 * 0.002, 9)
    result['note'] = 'Estimated values - CodeCarbon not available'
    
    return result


def get_hardware_info():
    """Get hardware information for better estimation."""
    info = {
        'cpu': 'unknown',
        'cpu_count': 1,
        'memory_gb': 0,
        'gpu': 'none'
    }
    
    try:
        import platform
        info['cpu'] = platform.processor()
        
        import os
        info['cpu_count'] = os.cpu_count() or 1
        
        # Try to get memory
        try:
            import psutil
            info['memory_gb'] = round(psutil.virtual_memory().total / (1024**3), 2)
        except:
            pass
            
        # Try to detect GPU
        try:
            import subprocess
            nvidia = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                   capture_output=True, text=True, timeout=5)
            if nvidia.returncode == 0:
                info['gpu'] = nvidia.stdout.strip()
        except:
            pass
            
    except:
        pass
    
    return info


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        # Read from stdin
        code = sys.stdin.read()
    
    result = run_with_codecarbon(code)
    print(json.dumps(result, indent=2))

