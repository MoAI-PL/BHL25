"""
GreenCode Demo - FastAPI Backend
A proof-of-concept visualization of the GreenCode PyCharm plugin.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import traceback

from utils.security import validate_code, get_safe_globals
from utils.hardware_emulator import execute_with_tracking

# Try to import eco_code_analyzer, fallback to mock if not available
try:
    from eco_code_analyzer import analyze_code, get_eco_score, get_improvement_suggestions
    ECO_ANALYZER_AVAILABLE = True
except ImportError:
    ECO_ANALYZER_AVAILABLE = False
    print("Warning: eco-code-analyzer not available, using mock analysis")


app = FastAPI(
    title="codeGreen Demo",
    description="PyCharm plugin visualization for code efficiency and carbon footprint analysis",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Request/Response models
class CodeRequest(BaseModel):
    code: str


class Issue(BaseModel):
    line: int
    type: str
    message: str
    severity: str = "warning"


class StaticAnalysisResponse(BaseModel):
    success: bool
    score: float  # 0-100
    score_label: str  # "excellent", "good", "fair", "poor"
    color: str  # "green", "yellow", "red"
    issues: List[Issue]
    suggestions: List[dict]
    message: str


class RuntimeAnalysisResponse(BaseModel):
    success: bool
    score: float  # 0-100
    score_label: str
    color: str
    emissions_g: float
    emissions_formatted: str
    duration_seconds: float
    energy_kwh: float
    power_watts: float
    issues: List[Issue]
    stdout: str
    stderr: str
    message: str


def get_score_color(score: float) -> tuple:
    """Get color and label based on score."""
    if score >= 70:
        return "green", "excellent" if score >= 85 else "good"
    elif score >= 40:
        return "yellow", "fair"
    else:
        return "red", "poor"


def mock_static_analysis(code: str) -> dict:
    """
    Fallback mock analysis when eco-code-analyzer is not available.
    Detects common inefficiency patterns.
    """
    issues = []
    lines = code.split('\n')
    score = 100.0
    
    for i, line in enumerate(lines, 1):
        line_lower = line.lower().strip()
        
        # Detect nested loops (O(n²) complexity)
        if 'for ' in line and any('for ' in prev for prev in lines[max(0, i-5):i-1]):
            issues.append({
                'line': i,
                'type': 'complexity',
                'message': 'Nested loop detected - O(n²) complexity. Consider using more efficient algorithms.',
                'severity': 'warning'
            })
            score -= 15
        
        # Detect bubble sort pattern
        if 'for i in range' in line_lower and 'for j in range' in code.lower():
            if 'a[j]' in code or 'arr[j]' in code or 'list[j]' in code:
                issues.append({
                    'line': i,
                    'type': 'algorithm',
                    'message': 'Bubble sort detected - O(n²) complexity. Use built-in sorted() for O(n log n).',
                    'severity': 'error'
                })
                score -= 20
                break
        
        # Detect append in loop (list growth)
        if '.append(' in line and any('for ' in prev for prev in lines[max(0, i-3):i]):
            issues.append({
                'line': i,
                'type': 'memory',
                'message': 'Appending in loop causes repeated memory allocation. Consider list comprehension.',
                'severity': 'info'
            })
            score -= 5
        
        # Detect range(len()) anti-pattern
        if 'range(len(' in line:
            issues.append({
                'line': i,
                'type': 'pythonic',
                'message': 'range(len()) is not Pythonic. Use enumerate() or iterate directly.',
                'severity': 'info'
            })
            score -= 5
        
        # Detect global variable usage
        if line.strip().startswith('global '):
            issues.append({
                'line': i,
                'type': 'design',
                'message': 'Global variable usage increases memory footprint and reduces code clarity.',
                'severity': 'warning'
            })
            score -= 10
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    return {
        'score': score,
        'issues': issues,
        'suggestions': [
            {
                'category': 'Algorithm Efficiency',
                'suggestion': 'Use built-in sorting functions which are optimized in C',
                'impact': 'high',
                'example': 'sorted(my_list) instead of custom bubble sort'
            },
            {
                'category': 'Loop Optimization', 
                'suggestion': 'Use list comprehensions for simple transformations',
                'impact': 'medium',
                'example': '[x*2 for x in range(100)] instead of append loop'
            }
        ] if issues else []
    }


def run_eco_analyzer(code: str) -> dict:
    """Run eco-code-analyzer or fallback to mock."""
    if ECO_ANALYZER_AVAILABLE:
        try:
            analysis_result = analyze_code(code)
            score = get_eco_score(analysis_result) * 100  # Convert to percentage
            suggestions = get_improvement_suggestions(analysis_result)
            
            # Convert suggestions to issues format
            issues = []
            for suggestion in suggestions:
                issues.append({
                    'line': suggestion.get('line', 1),
                    'type': suggestion.get('category', 'efficiency'),
                    'message': suggestion.get('suggestion', 'Consider optimizing this code'),
                    'severity': 'warning'
                })
            
            return {
                'score': score,
                'issues': issues,
                'suggestions': suggestions
            }
        except Exception as e:
            print(f"eco-code-analyzer error: {e}")
            return mock_static_analysis(code)
    else:
        return mock_static_analysis(code)


def detect_runtime_issues(code: str) -> List[dict]:
    """
    Detect code efficiency issues that would be flagged during runtime.
    More comprehensive than static analysis.
    """
    issues = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Nested loop detection
        indent_level = len(line) - len(line.lstrip())
        if 'for ' in line or 'while ' in line:
            # Check if there's an outer loop
            for j in range(i-1, 0, -1):
                prev_line = lines[j-1]
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                if prev_indent < indent_level and ('for ' in prev_line or 'while ' in prev_line):
                    issues.append({
                        'line': i,
                        'type': 'nested_loop',
                        'message': f'Nested loop at line {i} inside loop at line {j}. Time complexity: O(n²)',
                        'severity': 'error'
                    })
                    break
                elif prev_indent <= indent_level and prev_line.strip():
                    break
        
        # Inefficient comparison in loop
        if ('> ' in line or '< ' in line) and 'if' in line:
            for j in range(i-1, max(0, i-5), -1):
                if 'for ' in lines[j-1] or 'while ' in lines[j-1]:
                    issues.append({
                        'line': i,
                        'type': 'loop_comparison',
                        'message': 'Comparison inside loop. If comparing adjacent elements, consider more efficient sorting.',
                        'severity': 'warning'
                    })
                    break
        
        # Tuple swap pattern (often in bubble sort)
        if ', ' in line and ' = ' in line and line.count(',') >= 1:
            if '[j]' in line and '[j + 1]' in line or '[j]' in line and '[j+1]' in line:
                issues.append({
                    'line': i,
                    'type': 'swap_pattern',
                    'message': 'Element swap detected. Common in O(n²) sorting algorithms.',
                    'severity': 'info'
                })
        
        # range(len()) pattern
        if 'range(len(' in line:
            issues.append({
                'line': i,
                'type': 'anti_pattern',
                'message': 'range(len(x)) is inefficient. Use enumerate(x) or iterate directly.',
                'severity': 'warning'
            })
        
        # String concatenation in loop
        if '+=' in line and ("'" in line or '"' in line):
            issues.append({
                'line': i,
                'type': 'string_concat',
                'message': 'String concatenation with += creates new objects. Use join() or list.',
                'severity': 'warning'
            })
    
    return issues


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze-static", response_model=StaticAnalysisResponse)
async def analyze_static(request: CodeRequest):
    """
    Perform static code analysis for efficiency scoring.
    This simulates the plugin's real-time analysis as code is written.
    """
    code = request.code.strip()
    
    if not code:
        return StaticAnalysisResponse(
            success=False,
            score=0,
            score_label="none",
            color="gray",
            issues=[],
            suggestions=[],
            message="No code provided"
        )
    
    try:
        # Run analysis
        result = run_eco_analyzer(code)
        score = result['score']
        color, label = get_score_color(score)
        
        issues = [Issue(**issue) for issue in result['issues']]
        
        return StaticAnalysisResponse(
            success=True,
            score=round(score, 1),
            score_label=label,
            color=color,
            issues=issues,
            suggestions=result.get('suggestions', []),
            message=f"Static analysis complete. Efficiency score: {score:.1f}%"
        )
    
    except Exception as e:
        traceback.print_exc()
        return StaticAnalysisResponse(
            success=False,
            score=0,
            score_label="error",
            color="gray",
            issues=[],
            suggestions=[],
            message=f"Analysis error: {str(e)}"
        )


@app.post("/analyze-runtime", response_model=RuntimeAnalysisResponse)
async def analyze_runtime(request: CodeRequest):
    """
    Execute code and measure carbon emissions.
    This simulates the plugin's on-run analysis with codecarbon.
    """
    code = request.code.strip()
    
    if not code:
        return RuntimeAnalysisResponse(
            success=False,
            score=0,
            score_label="none",
            color="gray",
            emissions_g=0,
            emissions_formatted="0 g",
            duration_seconds=0,
            energy_kwh=0,
            power_watts=0,
            issues=[],
            stdout="",
            stderr="No code provided",
            message="No code provided"
        )
    
    # Security validation
    is_safe, violations = validate_code(code)
    
    if not is_safe:
        violation_issues = [
            Issue(
                line=v['line'],
                type=v['type'],
                message=v['message'],
                severity='error'
            )
            for v in violations
        ]
        
        return RuntimeAnalysisResponse(
            success=False,
            score=0,
            score_label="blocked",
            color="red",
            emissions_g=0,
            emissions_formatted="0 g",
            duration_seconds=0,
            energy_kwh=0,
            power_watts=0,
            issues=violation_issues,
            stdout="",
            stderr="Code contains security violations and cannot be executed.",
            message="Security check failed"
        )
    
    try:
        # Execute with emissions tracking
        safe_globals = get_safe_globals()
        emissions_data, stdout, stderr = execute_with_tracking(code, safe_globals)
        
        # Detect runtime-specific issues
        runtime_issues = detect_runtime_issues(code)
        issues = [Issue(**issue) for issue in runtime_issues]
        
        # Calculate efficiency score based on emissions and execution time
        # Lower emissions = higher score
        # Baseline: 0.00005g (0.05mg) for simple operations
        baseline_emissions = 0.00005
        emissions_g = emissions_data['emissions_g']
        
        if emissions_g <= baseline_emissions:
            score = 95.0
        else:
            # Log scale scoring - penalize high emissions
            import math
            ratio = emissions_g / baseline_emissions
            score = max(10, 100 - (math.log10(ratio) * 15))
        
        # Adjust score based on detected issues
        score -= len(runtime_issues) * 5
        score = max(0, min(100, score))
        
        color, label = get_score_color(score)
        
        # Format emissions for display - convert to mg for small values
        emissions_mg = emissions_g * 1000  # Convert g to mg
        if emissions_mg < 0.001:
            emissions_formatted = f"{emissions_mg * 1000:.4f} μg"  # micrograms
        elif emissions_mg < 1:
            emissions_formatted = f"{emissions_mg:.4f} mg"
        elif emissions_g < 1:
            emissions_formatted = f"{emissions_mg:.2f} mg"
        else:
            emissions_formatted = f"{emissions_g:.4f} g"
        
        return RuntimeAnalysisResponse(
            success=True,
            score=round(score, 1),
            score_label=label,
            color=color,
            emissions_g=emissions_g,
            emissions_formatted=emissions_formatted,
            duration_seconds=round(emissions_data['duration_seconds'], 4),
            energy_kwh=emissions_data['energy_kwh'],
            power_watts=emissions_data['power_watts']['total'],
            issues=issues,
            stdout=stdout,
            stderr=stderr,
            message=f"Execution complete. Carbon emissions: {emissions_formatted} CO₂"
        )
    
    except Exception as e:
        traceback.print_exc()
        return RuntimeAnalysisResponse(
            success=False,
            score=0,
            score_label="error",
            color="red",
            emissions_g=0,
            emissions_formatted="0 g",
            duration_seconds=0,
            energy_kwh=0,
            power_watts=0,
            issues=[],
            stdout="",
            stderr=str(e),
            message=f"Execution error: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "eco_analyzer_available": ECO_ANALYZER_AVAILABLE
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
