package com.hackathon.eco

import com.google.gson.Gson
import com.google.gson.JsonObject
import com.intellij.lang.annotation.AnnotationHolder
import com.intellij.lang.annotation.Annotator
import com.intellij.lang.annotation.HighlightSeverity
import com.intellij.psi.PsiElement
import com.intellij.psi.PsiFile
import java.io.File

class EcoAnnotator : Annotator {

    private val gson = Gson()

    override fun annotate(element: PsiElement, holder: AnnotationHolder) {
        // Only analyze at file level to avoid multiple calls
        if (element !is PsiFile) return
        
        val file = element as PsiFile
        if (!file.name.endsWith(".py")) return
        
        val code = file.text
        
        // Call Python analyzer
        val issues = analyzeWithPython(code)
        
        // Apply annotations based on Python analysis
        for (issue in issues) {
            try {
                val lineNumber = issue.get("line")?.asInt ?: 1
                val message = issue.get("message")?.asString ?: "Code efficiency issue"
                val severityStr = issue.get("severity")?.asString ?: "warning"
                
                val severity = when (severityStr) {
                    "error" -> HighlightSeverity.ERROR
                    "warning" -> HighlightSeverity.WARNING
                    else -> HighlightSeverity.WEAK_WARNING
                }
                
                val typeStr = issue.get("type")?.asString ?: ""
                val icon = when (typeStr) {
                    "inefficient_loop" -> "⚡"
                    "resource_leak" -> "💧"
                    "wildcard_import" -> "🗑️"
                    "nested_loop" -> "🔥"
                    else -> "⚠️"
                }
                
                val co2Impact = issue.get("co2_impact")?.asString ?: "unknown"
                
                // Find the element at this line
                val offset = getOffsetForLine(file, lineNumber)
                if (offset >= 0 && offset < file.textLength) {
                    val elementAtLine = file.findElementAt(offset)
                    if (elementAtLine != null) {
                        holder.newAnnotation(severity, "$icon Eco-Code: $message")
                            .range(elementAtLine)
                            .tooltip("$message\nCO2 Impact: $co2Impact")
                            .create()
                    }
                }
            } catch (e: Exception) {
                // Skip this issue if there's an error
            }
        }
    }
    
    private fun analyzeWithPython(code: String): List<JsonObject> {
        return try {
            // Find Python executable
            val pythonCmd = findPython()
            
            // Get the analyzer script from resources
            val scriptPath = getScriptPath("eco_analyzer.py")
            
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
            
            // Parse JSON array
            val jsonArray = gson.fromJson(output, Array<JsonObject>::class.java)
            jsonArray.toList()
        } catch (e: Exception) {
            // Fallback to simple regex-based analysis
            fallbackAnalysis(code)
        }
    }
    
    private fun fallbackAnalysis(code: String): List<JsonObject> {
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
                issue.addProperty("co2_impact", "medium")
                issues.add(issue)
            }
            
            if ("open(" in line && "with " !in line && "def " !in line) {
                val issue = JsonObject()
                issue.addProperty("line", lineNumber)
                issue.addProperty("severity", "warning")
                issue.addProperty("type", "resource_leak")
                issue.addProperty("message", "Resource leak risk")
                issue.addProperty("co2_impact", "low")
                issues.add(issue)
            }
        }
        
        return issues
    }
    
    private fun getOffsetForLine(file: PsiFile, lineNumber: Int): Int {
        val lines = file.text.split("\n")
        if (lineNumber <= 0 || lineNumber > lines.size) return -1
        
        var offset = 0
        for (i in 0 until lineNumber - 1) {
            offset += lines[i].length + 1 // +1 for newline
        }
        return offset
    }
    
    private fun findPython(): String {
        // Try common Python commands
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
        return "python3" // Default fallback
    }
    
    private fun getScriptPath(scriptName: String): String {
        // Try to get from resources
        val resource = javaClass.classLoader.getResource("scripts/$scriptName")
        if (resource != null) {
            return File(resource.toURI()).absolutePath
        }
        
        // Fallback: create temporary file
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
