package com.hackathon.eco

import com.google.gson.Gson
import com.google.gson.JsonObject
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.ui.DialogWrapper
import com.intellij.openapi.ui.Messages
import java.awt.Dimension
import java.io.File
import javax.swing.JComponent
import javax.swing.JScrollPane
import javax.swing.JTextArea

class EcoRun : AnAction() {

    private val gson = Gson()

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val document = editor.document
        
        // Get the entire file content
        val code = document.text
        
        // Calculate CO2 emissions
        val result = calculateCO2(code)
        
        if (result != null) {
            val co2Grams = result.get("estimated_co2_grams")?.asDouble ?: 0.0
            val energyKwh = result.get("estimated_energy_kwh")?.asDouble ?: 0.0
            val operations = result.getAsJsonObject("operations")
            
            val loops = operations?.get("loops")?.asInt ?: 0
            val fileOps = operations?.get("file_operations")?.asInt ?: 0
            val imports = operations?.get("imports")?.asInt ?: 0
            val functionCalls = operations?.get("function_calls")?.asInt ?: 0
            
            val message = buildString {
                appendLine("🌍 Carbon Footprint Estimation")
                appendLine("===================================")
                appendLine()
                appendLine("📊 Emissions:")
                appendLine("  • CO₂: ${String.format("%.6f", co2Grams)} g")
                appendLine("  • Energy: ${String.format("%.9f", energyKwh)} kWh")
                appendLine()
                appendLine("🔍 Code Analysis:")
                appendLine("  • Loops: $loops")
                appendLine("  • File Operations: $fileOps")
                appendLine("  • Imports: $imports")
                appendLine("  • Function Calls: $functionCalls")
                appendLine()
                appendLine("💡 Note: Static estimate based on code structure.")
                appendLine("Actual emissions vary with hardware and runtime.")
            }
            
            // Show custom dialog with more height
            val dialog = object : DialogWrapper(project, false) {
                init {
                    title = "Green Coding Assistant - CO₂ Analysis"
                    init()
                }
                
                override fun createCenterPanel(): JComponent {
                    val textArea = JTextArea(message).apply {
                        isEditable = false
                        lineWrap = true
                        wrapStyleWord = true
                        font = font.deriveFont(14f)
                    }
                    return JScrollPane(textArea).apply {
                        preferredSize = Dimension(450, 350)
                    }
                }
            }
            dialog.show()
        } else {
            Messages.showErrorDialog(
                project,
                "Could not calculate CO2 emissions. Make sure Python is installed.",
                "Green Coding Assistant"
            )
        }
    }
    
    private fun calculateCO2(code: String): JsonObject? {
        return try {
            // Find Python executable
            val pythonCmd = findPython()
            
            // Get the estimator script from resources
            val scriptPath = getScriptPath("co2_estimator.py")
            
            // Execute Python script
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
            process.waitFor()
            
            // Parse JSON
            gson.fromJson(output, JsonObject::class.java)
        } catch (e: Exception) {
            // Fallback to simple estimation
            fallbackEstimation(code)
        }
    }
    
    private fun fallbackEstimation(code: String): JsonObject {
        val lines = code.split("\n")
        var loopCount = 0
        var fileOps = 0
        var imports = 0
        
        for (line in lines) {
            if ("for " in line && "range(" in line) loopCount++
            if ("open(" in line) fileOps++
            if (line.trim().startsWith("import ") || line.trim().startsWith("from ")) imports++
        }
        
        // Simple estimation: 0.001g per loop, 0.00001g per file op, 0.00002g per import
        val totalCO2 = (loopCount * 0.001) + (fileOps * 0.00001) + (imports * 0.00002)
        
        val result = JsonObject()
        result.addProperty("estimated_co2_grams", totalCO2)
        result.addProperty("estimated_co2_kg", totalCO2 / 1000)
        result.addProperty("estimated_energy_kwh", totalCO2 * 0.002)
        
        val ops = JsonObject()
        ops.addProperty("loops", loopCount)
        ops.addProperty("file_operations", fileOps)
        ops.addProperty("imports", imports)
        ops.addProperty("function_calls", 0)
        result.add("operations", ops)
        
        result.addProperty("note", "Fallback estimation (Python not available)")
        
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
            return File(resource.toURI()).absolutePath
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
