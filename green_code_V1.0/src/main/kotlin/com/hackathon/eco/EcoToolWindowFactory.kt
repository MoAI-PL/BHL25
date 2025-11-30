package com.hackathon.eco

import com.google.gson.Gson
import com.google.gson.JsonObject
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.editor.EditorFactory
import com.intellij.openapi.editor.event.DocumentEvent
import com.intellij.openapi.editor.event.DocumentListener
import com.intellij.openapi.fileEditor.FileDocumentManager
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.fileEditor.FileEditorManagerListener
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.openapi.wm.ToolWindowManager
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.content.ContentFactory
import java.awt.*
import java.io.File
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import javax.swing.*

/**
 * Tool Window Factory for the Green Coding Assistant sidebar panel.
 * Shows eco score with dynamic colored icon that updates based on code analysis.
 */
class EcoToolWindowFactory : ToolWindowFactory {

    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val ecoToolWindow = EcoToolWindowPanel(project, toolWindow)
        val content = ContentFactory.getInstance().createContent(ecoToolWindow, "", false)
        toolWindow.contentManager.addContent(content)
    }
}

/**
 * Main panel for the Eco Tool Window.
 */
class EcoToolWindowPanel(
    private val project: Project,
    private val toolWindow: ToolWindow
) : JPanel(BorderLayout()) {

    private val gson = Gson()
    private var currentScore = 100
    private val scoreLabel = JLabel("--", SwingConstants.CENTER)
    private val statusLabel = JLabel("Open a Python file to analyze", SwingConstants.CENTER)
    private val detailsArea = JTextArea()
    private val analyzeButton = JButton("🔍 Analyze Code")
    private val runButton = JButton("▶ Run & Track CO₂")
    
    private val executor = Executors.newSingleThreadScheduledExecutor()
    private var lastAnalyzedCode = ""

    init {
        setupUI()
        setupListeners()
        
        // Initial analysis if a file is open
        ApplicationManager.getApplication().invokeLater {
            analyzeCurrentFile()
        }
    }

    private fun setupUI() {
        background = UIManager.getColor("Panel.background")
        
        // Score display panel
        val scorePanel = JPanel(BorderLayout()).apply {
            border = BorderFactory.createEmptyBorder(20, 20, 10, 20)
            isOpaque = false
        }
        
        // Large score display
        scoreLabel.apply {
            font = font.deriveFont(Font.BOLD, 48f)
            foreground = getScoreColor(currentScore)
        }
        
        val scoreTitleLabel = JLabel("Eco Score", SwingConstants.CENTER).apply {
            font = font.deriveFont(Font.PLAIN, 14f)
            foreground = UIManager.getColor("Label.disabledForeground")
        }
        
        val scoreContainer = JPanel(BorderLayout()).apply {
            isOpaque = false
            add(scoreLabel, BorderLayout.CENTER)
            add(scoreTitleLabel, BorderLayout.SOUTH)
        }
        
        scorePanel.add(scoreContainer, BorderLayout.CENTER)
        
        // Status label
        statusLabel.apply {
            font = font.deriveFont(Font.ITALIC, 12f)
            foreground = UIManager.getColor("Label.disabledForeground")
            border = BorderFactory.createEmptyBorder(5, 10, 10, 10)
        }
        
        // Button panel
        val buttonPanel = JPanel(GridLayout(2, 1, 5, 5)).apply {
            border = BorderFactory.createEmptyBorder(10, 20, 10, 20)
            isOpaque = false
        }
        
        analyzeButton.apply {
            addActionListener { analyzeCurrentFile() }
        }
        
        runButton.apply {
            addActionListener { runWithTracking() }
        }
        
        buttonPanel.add(analyzeButton)
        buttonPanel.add(runButton)
        
        // Details area
        detailsArea.apply {
            isEditable = false
            lineWrap = true
            wrapStyleWord = true
            background = UIManager.getColor("Panel.background")
            border = BorderFactory.createEmptyBorder(10, 10, 10, 10)
        }
        
        val detailsScroll = JBScrollPane(detailsArea).apply {
            border = BorderFactory.createTitledBorder("Analysis Details")
        }
        
        // Top panel with score and status
        val topPanel = JPanel(BorderLayout()).apply {
            isOpaque = false
            add(scorePanel, BorderLayout.CENTER)
            add(statusLabel, BorderLayout.SOUTH)
        }
        
        // Assemble
        add(topPanel, BorderLayout.NORTH)
        add(buttonPanel, BorderLayout.CENTER)
        add(detailsScroll, BorderLayout.SOUTH)
        
        // Make details area take remaining space
        detailsScroll.preferredSize = Dimension(250, 300)
    }

    private fun setupListeners() {
        // Listen for file changes
        project.messageBus.connect().subscribe(
            FileEditorManagerListener.FILE_EDITOR_MANAGER,
            object : FileEditorManagerListener {
                override fun fileOpened(source: FileEditorManager, file: VirtualFile) {
                    if (file.name.endsWith(".py")) {
                        scheduleAnalysis()
                    }
                }
                
                override fun selectionChanged(event: com.intellij.openapi.fileEditor.FileEditorManagerEvent) {
                    val file = event.newFile
                    if (file != null && file.name.endsWith(".py")) {
                        scheduleAnalysis()
                    } else {
                        updateUIForNonPython()
                    }
                }
            }
        )
        
        // Listen for document changes
        EditorFactory.getInstance().eventMulticaster.addDocumentListener(object : DocumentListener {
            override fun documentChanged(event: DocumentEvent) {
                val file = FileDocumentManager.getInstance().getFile(event.document)
                if (file != null && file.name.endsWith(".py")) {
                    scheduleAnalysis()
                }
            }
        }, project)
        
        // Listen for runtime score updates from carbon tracking
        project.messageBus.connect().subscribe(
            EcoScoreService.SCORE_UPDATED_TOPIC,
            object : EcoScoreService.ScoreUpdateListener {
                override fun onScoreUpdated(score: Int, emissionsGrams: Double, durationSeconds: Double, energyKwh: Double) {
                    ApplicationManager.getApplication().invokeLater {
                        updateUIFromRuntimeScore(score, emissionsGrams, durationSeconds, energyKwh)
                    }
                }
            }
        )
    }

    private var scheduledAnalysis: java.util.concurrent.ScheduledFuture<*>? = null
    
    private fun scheduleAnalysis() {
        scheduledAnalysis?.cancel(false)
        scheduledAnalysis = executor.schedule({
            ApplicationManager.getApplication().invokeLater {
                analyzeCurrentFile()
            }
        }, 500, TimeUnit.MILLISECONDS)
    }

    private fun analyzeCurrentFile() {
        val editor = FileEditorManager.getInstance(project).selectedTextEditor ?: run {
            updateUIForNonPython()
            return
        }
        
        val file = FileDocumentManager.getInstance().getFile(editor.document)
        if (file == null || !file.name.endsWith(".py")) {
            updateUIForNonPython()
            return
        }
        
        val code = editor.document.text
        
        // Skip if code hasn't changed
        if (code == lastAnalyzedCode) return
        lastAnalyzedCode = code
        
        statusLabel.text = "Analyzing..."
        
        // Run analysis in background
        executor.submit {
            val result = analyzeCode(code)
            ApplicationManager.getApplication().invokeLater {
                updateUI(result, file.name)
            }
        }
    }

    private fun updateUIForNonPython() {
        scoreLabel.text = "--"
        scoreLabel.foreground = UIManager.getColor("Label.disabledForeground")
        statusLabel.text = "Open a Python file to analyze"
        detailsArea.text = ""
        updateToolWindowIcon(null)
    }

    private fun updateUI(result: JsonObject?, fileName: String) {
        if (result == null) {
            statusLabel.text = "Analysis failed"
            return
        }
        
        val score = result.get("eco_score")?.asInt ?: 0
        currentScore = score
        
        // Update score display
        scoreLabel.text = "$score"
        scoreLabel.foreground = getScoreColor(score)
        
        // Update status
        val totalIssues = result.get("total_issues")?.asInt ?: 0
        statusLabel.text = if (totalIssues == 0) {
            "✅ $fileName - No issues!"
        } else {
            "📄 $fileName - $totalIssues issue${if (totalIssues > 1) "s" else ""}"
        }
        
        // Update details
        val details = buildString {
            val summary = result.getAsJsonObject("summary")
            val errors = summary?.get("errors")?.asInt ?: 0
            val warnings = summary?.get("warnings")?.asInt ?: 0
            val infos = summary?.get("info")?.asInt ?: 0
            
            appendLine("Score: $score/100 ${getScoreEmoji(score)}")
            appendLine()
            appendLine("Issues breakdown:")
            appendLine("  🔴 Errors: $errors")
            appendLine("  🟡 Warnings: $warnings")  
            appendLine("  🔵 Info: $infos")
            
            val issues = result.getAsJsonArray("issues")
            if (issues != null && issues.size() > 0) {
                appendLine()
                appendLine("─".repeat(30))
                
                for (issue in issues) {
                    val obj = issue.asJsonObject
                    val line = obj.get("line")?.asInt ?: 0
                    val msg = obj.get("message")?.asString ?: ""
                    val severity = obj.get("severity")?.asString ?: "info"
                    
                    if (line > 0) {
                        val icon = when (severity) {
                            "error" -> "🔴"
                            "warning" -> "🟡"
                            else -> "🔵"
                        }
                        appendLine()
                        appendLine("$icon Line $line:")
                        appendLine("   $msg")
                    }
                }
            }
        }
        
        detailsArea.text = details
        detailsArea.caretPosition = 0
        
        // Update tool window icon
        updateToolWindowIcon(score)
    }

    private fun updateToolWindowIcon(score: Int?) {
        ApplicationManager.getApplication().invokeLater {
            val icon = if (score != null) {
                EcoIconProvider.getColoredIcon(score)
            } else {
                EcoIconProvider.getGrayIcon()
            }
            toolWindow.setIcon(icon)
        }
    }

    /**
     * Update the UI based on actual runtime carbon tracking results.
     * This provides a more accurate score than static analysis.
     */
    private fun updateUIFromRuntimeScore(score: Int, emissionsGrams: Double, durationSeconds: Double, energyKwh: Double) {
        currentScore = score
        
        // Update score display with runtime indicator
        scoreLabel.text = "$score"
        scoreLabel.foreground = getScoreColor(score)
        
        // Update status to show it's from runtime measurement
        statusLabel.text = "⚡ Runtime score (actual measurement)"
        
        // Update details with runtime info
        val details = buildString {
            appendLine("Runtime Score: $score/100 ${getScoreEmoji(score)}")
            appendLine()
            appendLine("📊 Actual Measurements:")
            appendLine("  • CO₂: ${String.format("%.6f", emissionsGrams)} g")
            appendLine("  • Energy: ${String.format("%.9f", energyKwh)} kWh")
            appendLine("  • Duration: ${String.format("%.3f", durationSeconds)} s")
            appendLine()
            appendLine("─".repeat(30))
            appendLine()
            appendLine("This score is based on actual")
            appendLine("carbon emissions measured by")
            appendLine("CodeCarbon during execution.")
            appendLine()
            appendLine("Lower emissions = Higher score")
        }
        
        detailsArea.text = details
        detailsArea.caretPosition = 0
        
        // Update tool window icon
        updateToolWindowIcon(score)
    }

    private fun getScoreColor(score: Int): Color {
        return when {
            score >= 80 -> Color(76, 175, 80)   // Green
            score >= 50 -> Color(255, 193, 7)   // Yellow/Amber
            else -> Color(244, 67, 54)          // Red
        }
    }

    private fun getScoreEmoji(score: Int): String {
        return when {
            score >= 90 -> "🌟"
            score >= 70 -> "✅"
            score >= 50 -> "⚠️"
            else -> "🔴"
        }
    }

    private fun analyzeCode(code: String): JsonObject? {
        return try {
            val pythonCmd = findPython()
            val scriptPath = getScriptPath("ecocode_analyzer.py")
            
            val process = ProcessBuilder(pythonCmd, scriptPath)
                .redirectErrorStream(true)
                .start()
            
            process.outputStream.bufferedWriter().use { writer ->
                writer.write(code)
                writer.flush()
            }
            
            val output = process.inputStream.bufferedReader().use { it.readText() }
            process.waitFor(10, TimeUnit.SECONDS)
            
            gson.fromJson(output, JsonObject::class.java)
        } catch (e: Exception) {
            null
        }
    }

    private fun runWithTracking() {
        // Trigger the run with tracking action
        val editor = FileEditorManager.getInstance(project).selectedTextEditor ?: return
        val file = FileDocumentManager.getInstance().getFile(editor.document)
        
        if (file == null || !file.name.endsWith(".py")) {
            JOptionPane.showMessageDialog(
                this,
                "Please open a Python file first.",
                "Green Coding Assistant",
                JOptionPane.WARNING_MESSAGE
            )
            return
        }
        
        // Create and execute the action
        val action = EcoRunWithTracking()
        val dataContext = com.intellij.openapi.actionSystem.impl.SimpleDataContext.builder()
            .add(com.intellij.openapi.actionSystem.CommonDataKeys.PROJECT, project)
            .add(com.intellij.openapi.actionSystem.CommonDataKeys.EDITOR, editor)
            .add(com.intellij.openapi.actionSystem.CommonDataKeys.VIRTUAL_FILE, file)
            .build()
        
        val event = com.intellij.openapi.actionSystem.AnActionEvent.createFromDataContext(
            "EcoToolWindow",
            null,
            dataContext
        )
        
        action.actionPerformed(event)
    }

    private fun findPython(): String {
        val commands = listOf("python3", "python", "python.exe", "python3.exe")
        for (cmd in commands) {
            try {
                val process = ProcessBuilder(cmd, "--version").start()
                process.waitFor()
                if (process.exitValue() == 0) return cmd
            } catch (e: Exception) {
                continue
            }
        }
        return "python3"
    }

    private fun getScriptPath(scriptName: String): String {
        val resource = javaClass.classLoader.getResource("scripts/$scriptName")
        if (resource != null) {
            try {
                return File(resource.toURI()).absolutePath
            } catch (e: Exception) {
                // URI might not be a file
            }
        }
        
        val tempFile = File.createTempFile("eco_", "_$scriptName")
        tempFile.deleteOnExit()
        
        javaClass.classLoader.getResourceAsStream("scripts/$scriptName")?.use { input ->
            tempFile.outputStream().use { output ->
                input.copyTo(output)
            }
        }
        
        tempFile.setExecutable(true)
        return tempFile.absolutePath
    }
}

