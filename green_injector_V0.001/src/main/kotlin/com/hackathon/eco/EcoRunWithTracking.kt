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
import java.awt.BorderLayout
import java.awt.Dimension
import java.io.File
import javax.swing.*

/**
 * Action for running Python code with actual carbon emission tracking using CodeCarbon.
 * This executes the code and measures real CO2 emissions.
 */
class EcoRunWithTracking : AnAction() {

    private val gson = Gson()

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val document = editor.document
        val virtualFile = e.getData(CommonDataKeys.VIRTUAL_FILE)
        
        // Only allow Python files
        if (virtualFile != null && !virtualFile.name.endsWith(".py")) {
            Messages.showWarningDialog(
                project,
                "Carbon tracking is only available for Python files.",
                "Green Coding Assistant"
            )
            return
        }
        
        // Confirm execution
        val confirm = Messages.showYesNoDialog(
            project,
            "This will execute your Python code and track carbon emissions.\n\n" +
            "⚠️ The code will be run in a sandboxed environment.\n" +
            "Make sure you trust this code before running.\n\n" +
            "Continue?",
            "Run & Track CO₂ Emissions",
            Messages.getQuestionIcon()
        )
        
        if (confirm != Messages.YES) return
        
        val code = document.text
        
        // Run with tracking in background
        ProgressManager.getInstance().run(object : Task.Backgroundable(project, "Running with Carbon Tracking...", true) {
            override fun run(indicator: ProgressIndicator) {
                indicator.isIndeterminate = false
                indicator.fraction = 0.1
                indicator.text = "Starting CodeCarbon tracker..."
                
                indicator.fraction = 0.3
                indicator.text = "Executing Python code..."
                
                val result = runWithCodeCarbon(code)
                
                indicator.fraction = 0.9
                indicator.text = "Processing results..."
                
                // Show results on EDT
                com.intellij.openapi.application.ApplicationManager.getApplication().invokeLater {
                    showTrackingResults(project, result)
                }
            }
        })
    }
    
    private fun runWithCodeCarbon(code: String): JsonObject? {
        return try {
            val pythonCmd = findPython()
            val scriptPath = getScriptPath("codecarbon_tracker.py")
            
            val process = ProcessBuilder(pythonCmd, scriptPath)
                .redirectErrorStream(true)
                .start()
            
            // Write code to stdin
            process.outputStream.bufferedWriter().use { writer ->
                writer.write(code)
                writer.flush()
            }
            
            // Read JSON output
            val output = process.inputStream.bufferedReader().use { it.readText() }
            val exitCode = process.waitFor()
            
            // Parse JSON
            val result = gson.fromJson(output, JsonObject::class.java)
            result?.addProperty("exit_code", exitCode)
            result
        } catch (e: Exception) {
            val error = JsonObject()
            error.addProperty("success", false)
            error.addProperty("error", "Failed to run CodeCarbon: ${e.message}")
            error.addProperty("method", "error")
            error
        }
    }
    
    private fun showTrackingResults(project: com.intellij.openapi.project.Project, result: JsonObject?) {
        if (result == null) {
            Messages.showErrorDialog(project, "Failed to track emissions.", "Green Coding Assistant")
            return
        }
        
        val method = result.get("method")?.asString ?: "unknown"
        val emissionsGrams = result.get("emissions_grams")?.asDouble ?: 0.0
        val energyKwh = result.get("energy_kwh")?.asDouble ?: 0.0
        val durationSec = result.get("duration_seconds")?.asDouble ?: 0.0
        val cpuPower = result.get("cpu_power_watts")?.asDouble ?: 0.0
        val gpuPower = result.get("gpu_power_watts")?.asDouble ?: 0.0
        val ramPower = result.get("ram_power_watts")?.asDouble ?: 0.0
        val country = result.get("country_iso_code")?.asString ?: "unknown"
        val execOutput = result.get("execution_output")?.asString ?: ""
        
        val message = buildString {
            appendLine("🌍 Carbon Emission Tracking Report")
            appendLine("═══════════════════════════════════════")
            appendLine()
            
            if (method == "codecarbon") {
                appendLine("✅ Tracked with CodeCarbon (actual measurement)")
            }
            
            appendLine()
            appendLine("📊 Emissions:")
            appendLine("  • CO₂: ${String.format("%.9f", emissionsGrams)} g")
            appendLine("  • Energy: ${String.format("%.12f", energyKwh)} kWh")
            appendLine()
            
            appendLine("⏱️ Execution Time: ${String.format("%.3f", durationSec)} seconds")
            appendLine()
            
            if (cpuPower > 0 || gpuPower > 0 || ramPower > 0) {
                appendLine("⚡ Power Consumption:")
                if (cpuPower > 0) appendLine("  • CPU: ${String.format("%.2f", cpuPower)} W")
                if (gpuPower > 0) appendLine("  • GPU: ${String.format("%.2f", gpuPower)} W")
                if (ramPower > 0) appendLine("  • RAM: ${String.format("%.2f", ramPower)} W")
                appendLine()
            }
            
            if (country != "unknown") {
                appendLine("🌐 Location: $country")
                appendLine()
            }
            
            // Environmental equivalents
            appendLine("🌳 Environmental Impact Equivalent:")
            val treeDays = emissionsGrams / 22.0 // A tree absorbs ~22g CO2/day
            val carMeters = emissionsGrams / 0.21 // ~210g CO2 per km for car
            val lightbulbSec = energyKwh * 3600 / 0.01 // 10W LED bulb
            
            appendLine("  • Tree absorption: ${String.format("%.6f", treeDays)} days")
            appendLine("  • Car driving: ${String.format("%.4f", carMeters)} meters")
            appendLine("  • LED bulb (10W): ${String.format("%.3f", lightbulbSec)} seconds")
            
            if (execOutput.isNotEmpty()) {
                appendLine()
                appendLine("───────────────────────────────────────")
                appendLine("📤 Program Output:")
                appendLine("───────────────────────────────────────")
                val truncatedOutput = if (execOutput.length > 1000) {
                    execOutput.take(1000) + "\n... (truncated)"
                } else {
                    execOutput
                }
                appendLine(truncatedOutput)
            }
        }
        
        val dialog = object : DialogWrapper(project, false) {
            init {
                title = "Green Coding Assistant - Carbon Tracking Results"
                init()
            }
            
            override fun createCenterPanel(): JComponent {
                val panel = JPanel(BorderLayout())
                
                val textArea = JTextArea(message).apply {
                    isEditable = false
                    lineWrap = true
                    wrapStyleWord = true
                    font = font.deriveFont(13f)
                }
                
                panel.add(JScrollPane(textArea), BorderLayout.CENTER)
                panel.preferredSize = Dimension(550, 500)
                
                return panel
            }
        }
        dialog.show()
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

