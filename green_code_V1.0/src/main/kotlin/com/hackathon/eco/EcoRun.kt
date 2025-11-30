package com.hackathon.eco

import com.google.gson.Gson
import com.google.gson.JsonObject
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.progress.ProgressIndicator
import com.intellij.openapi.progress.ProgressManager
import com.intellij.openapi.progress.Task
import com.intellij.openapi.ui.DialogWrapper
import com.intellij.openapi.ui.Messages
import java.awt.Dimension
import java.io.File
import javax.swing.JComponent
import javax.swing.JScrollPane
import javax.swing.JTextArea

/**
 * Action for static CO2 estimation (analyzes code without executing).
 * Uses eco-code-analyzer library for static analysis.
 */
class EcoRun : AnAction() {

    private val gson = Gson()

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val document = editor.document
        
        // Get the entire file content
        val code = document.text
        
        // Run analysis in background
        ProgressManager.getInstance().run(object : Task.Backgroundable(project, "Analyzing Code Efficiency...", false) {
            override fun run(indicator: ProgressIndicator) {
                indicator.isIndeterminate = true
                indicator.text = "Running eco-code analysis..."
                
                val result = analyzeCode(code)
                
                // Show results on EDT
                com.intellij.openapi.application.ApplicationManager.getApplication().invokeLater {
                    showAnalysisResults(project, result)
                }
            }
        })
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
            process.waitFor()
            
            gson.fromJson(output, JsonObject::class.java)
        } catch (e: Exception) {
            fallbackAnalysis(code)
        }
    }
    
    private fun showAnalysisResults(project: com.intellij.openapi.project.Project, result: JsonObject?) {
        if (result == null) {
            Messages.showErrorDialog(project, "Analysis failed.", "Green Coding Assistant")
            return
        }
        
        val ecoScore = result.get("eco_score")?.asInt ?: 0
        val totalIssues = result.get("total_issues")?.asInt ?: 0
        val issues = result.getAsJsonArray("issues")
        val summary = result.getAsJsonObject("summary")
        
        val errors = summary?.get("errors")?.asInt ?: 0
        val warnings = summary?.get("warnings")?.asInt ?: 0
        val infos = summary?.get("info")?.asInt ?: 0
        
        val message = buildString {
            appendLine("🌿 Eco Code Analysis Report")
            appendLine("═══════════════════════════════════════")
            appendLine()
            appendLine("📊 Eco Score: $ecoScore/100 ${getScoreEmoji(ecoScore)}")
            appendLine()
            appendLine("📋 Summary:")
            appendLine("  • Total Issues: $totalIssues")
            appendLine("  • 🔴 Errors: $errors")
            appendLine("  • 🟡 Warnings: $warnings")
            appendLine("  • 🔵 Info: $infos")
            appendLine()
            
            if (issues != null && issues.size() > 0) {
                appendLine("🔍 Issues Found:")
                appendLine("───────────────────────────────────────")
                
                for (issue in issues) {
                    val obj = issue.asJsonObject
                    val line = obj.get("line")?.asInt ?: 0
                    val severity = obj.get("severity")?.asString ?: "info"
                    val type = obj.get("type")?.asString ?: ""
                    val msg = obj.get("message")?.asString ?: ""
                    val suggestion = obj.get("suggestion")?.asString ?: ""
                    val impact = obj.get("co2_impact")?.asString ?: "low"
                    
                    val icon = when (severity) {
                        "error" -> "🔴"
                        "warning" -> "🟡"
                        else -> "🔵"
                    }
                    
                    if (line > 0) {
                        appendLine()
                        appendLine("$icon Line $line: $msg")
                        if (suggestion.isNotEmpty()) {
                            appendLine("   💡 $suggestion")
                        }
                        appendLine("   ⚡ CO₂ Impact: $impact")
                    }
                }
            } else {
                appendLine("✅ No issues found! Your code is eco-friendly.")
            }
            
            appendLine()
            appendLine("───────────────────────────────────────")
            appendLine("💡 Tip: Use 'Run & Track CO₂' to measure")
            appendLine("   actual emissions during execution.")
        }
        
        val dialog = object : DialogWrapper(project, false) {
            init {
                title = "Green Coding Assistant - Eco Analysis"
                init()
            }
            
            override fun createCenterPanel(): JComponent {
                val textArea = JTextArea(message).apply {
                    isEditable = false
                    lineWrap = true
                    wrapStyleWord = true
                }
                return JScrollPane(textArea).apply {
                    preferredSize = Dimension(500, 450)
                }
            }
        }
        dialog.show()
    }
    
    private fun getScoreEmoji(score: Int): String {
        return when {
            score >= 90 -> "🌟 Excellent!"
            score >= 70 -> "✅ Good"
            score >= 50 -> "⚠️ Needs improvement"
            else -> "🔴 Poor"
        }
    }
    
    private fun fallbackAnalysis(code: String): JsonObject {
        val issues = mutableListOf<JsonObject>()
        val lines = code.split("\n")
        
        for ((i, line) in lines.withIndex()) {
            val lineNumber = i + 1
            val trimmed = line.trim()
            
            if (trimmed.startsWith("for ") && "range(" in trimmed) {
                val issue = JsonObject()
                issue.addProperty("line", lineNumber)
                issue.addProperty("severity", "warning")
                issue.addProperty("type", "inefficient_loop")
                issue.addProperty("message", "Inefficient loop detected")
                issue.addProperty("suggestion", "Consider using NumPy or list comprehension")
                issue.addProperty("co2_impact", "medium")
                issues.add(issue)
            }
            
            if ("open(" in line && "with " !in line && "def " !in line) {
                val issue = JsonObject()
                issue.addProperty("line", lineNumber)
                issue.addProperty("severity", "warning")
                issue.addProperty("type", "resource_leak")
                issue.addProperty("message", "Resource leak risk - file not using context manager")
                issue.addProperty("suggestion", "Use 'with open(...) as f:' pattern")
                issue.addProperty("co2_impact", "low")
                issues.add(issue)
            }
        }
        
        val result = JsonObject()
        result.addProperty("eco_score", 100 - (issues.size * 10))
        result.addProperty("total_issues", issues.size)
        
        val summary = JsonObject()
        summary.addProperty("errors", 0)
        summary.addProperty("warnings", issues.size)
        summary.addProperty("info", 0)
        result.add("summary", summary)
        
        val issuesArray = com.google.gson.JsonArray()
        issues.forEach { issuesArray.add(it) }
        result.add("issues", issuesArray)
        
        result.addProperty("note", "Fallback analysis (Python analyzer not available)")
        
        return result
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
                // URI might not be a file (e.g., in JAR)
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
