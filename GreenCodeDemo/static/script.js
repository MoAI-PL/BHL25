/**
 * codeGreen Demo - Frontend JavaScript
 * Handles UI interactions and API communication
 */

// DOM Elements
const codeEditor = document.getElementById('code-editor');
const loadDummyBtn = document.getElementById('load-dummy-btn');
const analyzeRuntimeBtn = document.getElementById('analyze-runtime-btn');
const lineNumbers = document.getElementById('line-numbers');
const runStatus = document.getElementById('run-status');
const consoleOutput = document.getElementById('console-output');

// Static analysis banner elements
const staticScoreBar = document.getElementById('static-score-bar');
const staticIcon = document.getElementById('static-icon');
const staticText = document.getElementById('static-text');

// Results section
const resultsSection = document.getElementById('results-section');
const runtimePanel = document.getElementById('runtime-panel');
const issuesPanel = document.getElementById('issues-panel');
const suggestionsPanel = document.getElementById('suggestions-panel');

// Runtime metrics
const runtimeBadge = document.getElementById('runtime-badge');
const emissionsValue = document.getElementById('emissions-value');
const runtimeScoreValue = document.getElementById('runtime-score-value');
const durationValue = document.getElementById('duration-value');
const powerValue = document.getElementById('power-value');
const runtimeScoreFill = document.getElementById('runtime-score-fill');

// Output section
const outputSection = document.getElementById('output-section');
const programOutput = document.getElementById('program-output');

// Lists
const issuesList = document.getElementById('issues-list');
const issuesCount = document.getElementById('issues-count');
const suggestionsList = document.getElementById('suggestions-list');

// Loading
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');

// Toast container
const toastContainer = document.getElementById('toast-container');

// Debounce timer for auto-analysis
let analysisTimer = null;
const ANALYSIS_DELAY = 800; // ms delay after typing stops

// Dummy code for demonstration
const DUMMY_CODE = `def bubble_sort(a):
    for i in range(len(a)):
        for j in range(len(a) - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a

print(bubble_sort([5,3,8,1,2]))`;

/**
 * Log a message to the console output display
 * @param {string} message - The message to display
 * @param {string} type - 'info', 'success', 'warning', 'error'
 * @param {number} duration - How long to show (ms)
 */
function consoleLog(message, type = 'info', duration = 2500) {
    const line = document.createElement('div');
    line.className = `console-line ${type}`;
    line.textContent = message;
    consoleOutput.appendChild(line);
    
    // Limit visible lines to 5
    while (consoleOutput.children.length > 5) {
        consoleOutput.removeChild(consoleOutput.firstChild);
    }
    
    // Fade out and remove after duration
    setTimeout(() => {
        line.classList.add('fading');
        setTimeout(() => {
            if (line.parentNode) {
                line.remove();
            }
        }, 500);
    }, duration);
}

/**
 * Update line numbers to match code editor content
 */
function updateLineNumbers() {
    const lines = codeEditor.value.split('\n').length;
    const numbers = [];
    for (let i = 1; i <= Math.max(lines, 1); i++) {
        numbers.push(i);
    }
    lineNumbers.textContent = numbers.join('\n');
}

/**
 * Sync scroll between editor and line numbers
 */
function syncScroll() {
    lineNumbers.scrollTop = codeEditor.scrollTop;
}

/**
 * Show loading overlay
 */
function showLoading(text = 'Analyzing...') {
    loadingText.textContent = text;
    loadingOverlay.classList.remove('hidden');
    runStatus.textContent = 'Running...';
    runStatus.className = 'run-status analyzing';
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Update score bar display
 */
function updateScoreBar(fillElement, valueElement, score, color) {
    fillElement.style.width = `${score}%`;
    fillElement.className = `score-bar-fill ${color}`;
    if (valueElement && valueElement.textContent !== undefined) {
        valueElement.textContent = `${score.toFixed(1)}%`;
        valueElement.className = `score-value ${color}`;
    }
    
    // Update score bar background color class
    const scoreBar = fillElement.closest('.score-bar');
    if (scoreBar) {
        scoreBar.classList.remove('green-bg', 'yellow-bg', 'red-bg');
        scoreBar.classList.add(`${color}-bg`);
    }
}

/**
 * Render issues list
 */
function renderIssues(issues) {
    issuesList.innerHTML = '';
    
    if (issues.length === 0) {
        issuesPanel.classList.add('hidden');
        return;
    }
    
    issuesPanel.classList.remove('hidden');
    issuesCount.textContent = issues.length;
    
    issues.forEach(issue => {
        const li = document.createElement('li');
        li.className = 'issue-item';
        li.innerHTML = `
            <span class="issue-line">Line ${issue.line}</span>
            <div class="issue-content">
                <span class="issue-type ${issue.severity}">${issue.type}</span>
                <p class="issue-message">${issue.message}</p>
            </div>
        `;
        issuesList.appendChild(li);
    });
}

/**
 * Render suggestions list
 */
function renderSuggestions(suggestions) {
    suggestionsList.innerHTML = '';
    
    if (!suggestions || suggestions.length === 0) {
        suggestionsPanel.classList.add('hidden');
        return;
    }
    
    suggestionsPanel.classList.remove('hidden');
    
    suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.className = 'suggestion-item';
        li.innerHTML = `
            <div class="suggestion-category">${suggestion.category || 'Optimization'}</div>
            <p class="suggestion-text">${suggestion.suggestion || suggestion.message || ''}</p>
            ${suggestion.example ? `<code class="suggestion-example">${suggestion.example}</code>` : ''}
        `;
        suggestionsList.appendChild(li);
    });
}

/**
 * Update static analysis banner with qualitative feedback
 */
function updateStaticBanner(score, issueCount) {
    staticScoreBar.classList.remove('hidden', 'optimal', 'warning', 'inefficient');
    
    if (score === 100 && issueCount === 0) {
        // Only show green "optimal" for perfect score with no issues
        staticScoreBar.classList.add('optimal');
        staticIcon.textContent = '✓';
        staticText.textContent = 'Code looks optimal';
    } else if (issueCount === 0) {
        // No issues but not perfect - still show warning
        staticScoreBar.classList.add('warning');
        staticIcon.textContent = '⚡';
        staticText.textContent = 'Minor optimizations possible';
    } else {
        // Any issues found - show inefficient
        staticScoreBar.classList.add('inefficient');
        staticIcon.textContent = '⚠';
        staticText.textContent = `Improvements possible (${issueCount} issue${issueCount !== 1 ? 's' : ''} found)`;
    }
}

/**
 * Perform static analysis (auto-triggered as user types)
 */
async function performStaticAnalysis(silent = false) {
    const code = codeEditor.value.trim();
    
    if (!code) {
        staticScoreBar.classList.add('hidden');
        return;
    }
    
    // Don't show loading overlay for auto-analysis
    if (!silent) {
        showLoading('Performing static analysis...');
    } else {
        consoleLog('analyzing code...', 'info', 1500);
    }
    
    try {
        const response = await fetch('/analyze-static', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update static banner with qualitative feedback
            const issueCount = data.issues ? data.issues.length : 0;
            updateStaticBanner(data.score, issueCount);
            
            // Console log the result
            if (issueCount === 0) {
                consoleLog('static: code looks good', 'success', 2000);
            } else {
                consoleLog(`static: ${issueCount} issue(s) found`, 'warning', 2000);
            }
        } else if (!silent) {
            showToast(data.message || 'Analysis failed', 'error');
            consoleLog('analysis failed', 'error');
        }
    } catch (error) {
        console.error('Static analysis error:', error);
        if (!silent) {
            showToast('Failed to analyze code. Please try again.', 'error');
        }
        consoleLog('connection error', 'error');
    } finally {
        if (!silent) {
            hideLoading();
        }
    }
}

/**
 * Debounced auto-analysis when user types
 */
function scheduleAutoAnalysis() {
    if (analysisTimer) {
        clearTimeout(analysisTimer);
    }
    analysisTimer = setTimeout(() => {
        performStaticAnalysis(true);
    }, ANALYSIS_DELAY);
}

/**
 * Perform runtime analysis
 */
async function performRuntimeAnalysis() {
    const code = codeEditor.value.trim();
    
    if (!code) {
        showToast('Please enter some code to run', 'warning');
        consoleLog('error: no code to run', 'error');
        return;
    }
    
    showLoading('Executing code & measuring emissions...');
    consoleLog('executing code...', 'info');
    
    try {
        const response = await fetch('/analyze-runtime', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
        });
        
        const data = await response.json();
        
        // Show results section
        resultsSection.classList.remove('hidden');
        
        if (data.success) {
            // Console log execution results
            consoleLog('execution complete', 'success', 1500);
            consoleLog(`runtime: ${(data.duration_seconds * 1000).toFixed(2)}ms`, 'info', 2500);
            consoleLog(`emissions: ${data.emissions_formatted} CO₂`, 'info', 2500);
            
            const colorType = data.color === 'green' ? 'success' : data.color === 'yellow' ? 'warning' : 'error';
            consoleLog(`efficiency: ${data.score.toFixed(0)}%`, colorType, 3000);
            
            if (data.issues && data.issues.length > 0) {
                consoleLog(`detected ${data.issues.length} inefficiency(s)`, 'warning', 3000);
            }
            
            // Show runtime panel
            runtimePanel.classList.remove('hidden');
            
            // Update badge
            runtimeBadge.textContent = `${data.score.toFixed(1)}%`;
            runtimeBadge.className = `panel-badge ${data.color}`;
            
            // Update metrics
            emissionsValue.textContent = data.emissions_formatted + ' CO₂';
            runtimeScoreValue.textContent = `${data.score.toFixed(1)}%`;
            
            // Format duration
            const durationMs = data.duration_seconds * 1000;
            if (durationMs < 1) {
                durationValue.textContent = `${(durationMs * 1000).toFixed(2)} μs`;
            } else if (durationMs < 1000) {
                durationValue.textContent = `${durationMs.toFixed(2)} ms`;
            } else {
                durationValue.textContent = `${data.duration_seconds.toFixed(2)} s`;
            }
            
            powerValue.textContent = `${data.power_watts.toFixed(1)} W`;
            
            // Update runtime score bar
            updateScoreBar(runtimeScoreFill, { textContent: '', className: '' }, data.score, data.color);
            
            // Show output if any
            if (data.stdout || data.stderr) {
                outputSection.classList.remove('hidden');
                if (data.stderr && !data.stdout) {
                    programOutput.textContent = data.stderr;
                    programOutput.className = 'output-box error';
                } else {
                    programOutput.textContent = data.stdout || '(No output)';
                    programOutput.className = 'output-box';
                }
            } else {
                outputSection.classList.add('hidden');
            }
            
            // Render issues
            renderIssues(data.issues);
            
            // Update run status
            runStatus.textContent = `Done: ${data.score.toFixed(0)}% efficiency`;
            runStatus.className = `run-status ${data.color === 'green' ? 'success' : data.color === 'yellow' ? 'analyzing' : 'error'}`;
            
            showToast(`Code executed! Emissions: ${data.emissions_formatted} CO₂`, 
                data.color === 'green' ? 'success' : data.color === 'yellow' ? 'warning' : 'error');
        } else {
            // Console log error
            consoleLog('execution blocked', 'error');
            if (data.issues && data.issues.length > 0) {
                consoleLog(`security: ${data.issues[0].message.substring(0, 40)}...`, 'error', 3500);
            }
            
            // Show error state
            runtimePanel.classList.add('hidden');
            
            // Show security violations or errors as issues
            renderIssues(data.issues);
            
            // Hide suggestions on error
            suggestionsPanel.classList.add('hidden');
            
            // Update run status
            runStatus.textContent = 'Error';
            runStatus.className = 'run-status error';
            
            showToast(data.message || 'Execution failed', 'error');
        }
    } catch (error) {
        console.error('Runtime analysis error:', error);
        consoleLog('connection error', 'error');
        runStatus.textContent = 'Error';
        runStatus.className = 'run-status error';
        showToast('Failed to execute code. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Load dummy code into editor with typing animation effect
 */
function loadDummyCode() {
    // Console log the action
    consoleLog('loading example code...', 'info', 1500);
    
    codeEditor.value = DUMMY_CODE;
    updateLineNumbers();
    
    // Reset UI
    resultsSection.classList.add('hidden');
    runtimePanel.classList.add('hidden');
    issuesPanel.classList.add('hidden');
    suggestionsPanel.classList.add('hidden');
    runStatus.textContent = 'Ready';
    runStatus.className = 'run-status';
    
    // Simulate writing effect with console logs
    setTimeout(() => consoleLog('writing code...', 'info', 1500), 200);
    setTimeout(() => consoleLog('bubble_sort() loaded', 'success', 2000), 600);
    
    showToast('Loaded example bubble sort code', 'success');
    
    // Focus editor and trigger auto-analysis
    codeEditor.focus();
    scheduleAutoAnalysis();
}

// Event Listeners
loadDummyBtn.addEventListener('click', loadDummyCode);
analyzeRuntimeBtn.addEventListener('click', performRuntimeAnalysis);

// Code editor events
codeEditor.addEventListener('input', () => {
    updateLineNumbers();
    scheduleAutoAnalysis();
});
codeEditor.addEventListener('scroll', syncScroll);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to run
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        performRuntimeAnalysis();
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateLineNumbers();
    
    // Welcome console messages
    setTimeout(() => consoleLog('codeGreen initialized', 'success', 2500), 300);
    setTimeout(() => consoleLog('ready for analysis', 'info', 2000), 800);
    
    setTimeout(() => {
        showToast('Welcome! Click "Load Example" to get started 🌱', 'success', 5000);
    }, 500);
});
