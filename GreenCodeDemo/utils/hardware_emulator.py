"""
Hardware emulator for codecarbon in containerized environments.
Provides simulated power consumption values when real hardware sensors are unavailable.
"""

import time
from typing import Optional, Tuple
from contextlib import contextmanager
from io import StringIO
import sys


class EmulatedEmissionsTracker:
    """
    Emulated emissions tracker that simulates hardware power consumption.
    Uses realistic power scaling based on actual script complexity and runtime.
    """
    
    # Carbon intensity (gCO2/kWh) - Using USA average
    # Source: EPA eGRID 2021
    CARBON_INTENSITY_G_PER_KWH = 400.0
    
    # Realistic power ranges for a single Python process
    # A simple Python script uses a fraction of total system power
    MIN_POWER_WATTS = 0.5   # Idle/minimal script
    MAX_POWER_WATTS = 15.0  # CPU-intensive script (single core)
    
    # Minimum emissions baseline (in grams CO2)
    # Even the fastest script requires some energy to parse, compile, and execute
    # This represents ~0.01-0.05g which is realistic for a simple script
    MIN_EMISSIONS_MG = 0.015  # 0.015 mg minimum
    
    def __init__(self, project_name: str = "greencode_demo"):
        self.project_name = project_name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.is_running = False
        
        # Tracking metrics
        self.duration_seconds: float = 0.0
        self.energy_kwh: float = 0.0
        self.emissions_kg: float = 0.0
        self.emissions_g: float = 0.0
        self.power_watts: float = 0.0
        
        # CPU utilization simulation
        self.cpu_utilization: float = 0.0
    
    def start(self) -> None:
        """Start tracking emissions."""
        self.start_time = time.perf_counter()
        self.is_running = True
    
    def stop(self) -> float:
        """
        Stop tracking and calculate emissions.
        
        Returns:
            Emissions in kg CO2
        """
        if not self.is_running:
            return 0.0
        
        self.end_time = time.perf_counter()
        self.is_running = False
        
        # Calculate duration
        self.duration_seconds = self.end_time - self.start_time
        
        # Estimate power based on execution time (realistic scaling)
        # Very fast scripts (<1ms) = minimal power
        # Longer scripts = more CPU work = more power
        if self.duration_seconds < 0.001:  # < 1ms
            self.power_watts = self.MIN_POWER_WATTS
            self.cpu_utilization = 0.02
        elif self.duration_seconds < 0.01:  # < 10ms
            self.power_watts = 1.0
            self.cpu_utilization = 0.05
        elif self.duration_seconds < 0.1:  # < 100ms
            self.power_watts = 2.5
            self.cpu_utilization = 0.10
        elif self.duration_seconds < 1.0:  # < 1s
            self.power_watts = 5.0
            self.cpu_utilization = 0.20
        elif self.duration_seconds < 5.0:  # < 5s
            self.power_watts = 8.0
            self.cpu_utilization = 0.35
        else:  # >= 5s (CPU intensive)
            self.power_watts = self.MAX_POWER_WATTS
            self.cpu_utilization = 0.50
        
        # Calculate energy consumed (kWh)
        # Use a minimum effective duration to account for Python startup/parsing overhead
        effective_duration = max(self.duration_seconds, 0.005)  # At least 5ms equivalent
        hours = effective_duration / 3600.0
        self.energy_kwh = (self.power_watts * hours)
        
        # Calculate carbon emissions with minimum baseline
        calculated_emissions_g = self.energy_kwh * self.CARBON_INTENSITY_G_PER_KWH
        
        # Apply minimum emissions (convert MIN_EMISSIONS_MG to grams)
        self.emissions_g = max(calculated_emissions_g, self.MIN_EMISSIONS_MG / 1000.0)
        self.emissions_kg = self.emissions_g / 1000.0
        
        return self.emissions_kg
    
    def get_emissions_data(self) -> dict:
        """
        Get detailed emissions data.
        
        Returns:
            Dictionary with emissions metrics
        """
        return {
            'project_name': self.project_name,
            'duration_seconds': round(self.duration_seconds, 6),
            'energy_kwh': self.energy_kwh,
            'emissions_kg': self.emissions_kg,
            'emissions_g': round(self.emissions_g, 9),
            'cpu_utilization': self.cpu_utilization,
            'power_watts': {
                'cpu': self.power_watts * 0.85,  # ~85% is CPU
                'ram': self.power_watts * 0.15,  # ~15% is RAM
                'base': 0,
                'total': self.power_watts
            },
            'carbon_intensity_g_per_kwh': self.CARBON_INTENSITY_G_PER_KWH,
            'region': 'USA (average)',
            'emulated': True
        }


@contextmanager
def track_emissions(project_name: str = "greencode_demo"):
    """
    Context manager for tracking emissions during code execution.
    
    Usage:
        with track_emissions() as tracker:
            # Run code here
            result = some_function()
        
        emissions_data = tracker.get_emissions_data()
    """
    tracker = EmulatedEmissionsTracker(project_name=project_name)
    tracker.start()
    try:
        yield tracker
    finally:
        tracker.stop()


def execute_with_tracking(code: str, safe_globals: dict, timeout: float = 10.0) -> Tuple[dict, str, str]:
    """
    Execute code with emissions tracking and output capture.
    
    Args:
        code: Python code to execute
        safe_globals: Restricted globals dict for execution
        timeout: Maximum execution time in seconds
        
    Returns:
        Tuple of (emissions_data, stdout, stderr)
    """
    # Capture stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    
    tracker = EmulatedEmissionsTracker(project_name="user_code")
    error_message = ""
    
    try:
        tracker.start()
        
        # Execute with timeout (simplified - in production use multiprocessing)
        local_vars = {}
        exec(code, safe_globals, local_vars)
        
        tracker.stop()
        
    except Exception as e:
        tracker.stop()
        error_message = f"{type(e).__name__}: {str(e)}"
        sys.stderr.write(error_message)
    
    finally:
        stdout_value = sys.stdout.getvalue()
        stderr_value = sys.stderr.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    return tracker.get_emissions_data(), stdout_value, stderr_value
