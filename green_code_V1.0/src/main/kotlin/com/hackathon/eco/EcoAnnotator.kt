package com.hackathon.eco

import com.google.gson.Gson
import com.google.gson.JsonObject
import com.intellij.lang.annotation.AnnotationHolder
import com.intellij.lang.annotation.Annotator
import com.intellij.lang.annotation.HighlightSeverity
import com.intellij.psi.PsiElement
import com.intellij.psi.PsiFile
import java.io.File
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.TimeUnit

/**
 * Real-time code annotator that uses eco-code-analyzer library
 * to highlight energy efficiency issues directly in the editor.
 */
class EcoAnnotator : Annotator {

    private val gson = Gson()
    
    // Cache analysis results to avoid re-analyzing unchanged code
    private val analysisCache = ConcurrentHashMap<Int, CachedAnalysis>()
    
    private data class CachedAnalysis(
        val codeHash: Int,
        val issues: List<JsonObject>,
        val timestamp: Long
    )

    override fun annotate(element: PsiElement, holder: AnnotationHolder) {
        // Only analyze at file level to avoid multiple calls
        if (element !is PsiFile) return
        
        val file = element as PsiFile
        if (!file.name.endsWith(".py")) return
        
        val code = file.text
        val codeHash = code.hashCode()
        
        // Check cache first
        val cached = analysisCache[file.hashCode()]
        val issues = if (cached != null && 
                        cached.codeHash == codeHash && 
                        System.currentTimeMillis() - cached.timestamp < TimeUnit.SECONDS.toMillis(30)) {
            cached.issues
        } else {
            // Analyze with eco-code-analyzer
            val newIssues = analyzeWithEcoCode(code)
            analysisCache[file.hashCode()] = CachedAnalysis(codeHash, newIssues, System.currentTimeMillis())
            newIssues
        }
        
        // Apply annotations based on analysis
        for (issue in issues) {
            try {
                val lineNumber = issue.get("line")?.asInt ?: continue
                if (lineNumber <= 0) continue  // Skip eco_score and other meta info
                
                val message = issue.get("message")?.asString ?: "Code efficiency issue"
                val severityStr = issue.get("severity")?.asString ?: "warning"
                val suggestion = issue.get("suggestion")?.asString ?: ""
                
                val severity = when (severityStr) {
                    "error" -> HighlightSeverity.ERROR
                    "warning" -> HighlightSeverity.WARNING
                    "info" -> HighlightSeverity.WEAK_WARNING
                    else -> HighlightSeverity.WEAK_WARNING
                }
                
                val typeStr = issue.get("type")?.asString ?: ""
                val icon = when (typeStr) {
                    "inefficient_loop", "large_loop", "medium_loop" -> "⚡"
                    "resource_leak" -> "💧"
                    "wildcard_import" -> "📦"
                    "nested_loop" -> "🔥"
                    "string_concat_loop" -> "📝"
                    "infinite_loop_risk" -> "♾️"
                    "recursion" -> "🔄"
                    "print_in_loop" -> "🖨️"
                    "full_file_read" -> "📄"
                    else -> "⚠️"
                }
                
                val co2Impact = issue.get("co2_impact")?.asString ?: "unknown"
                val impactEmoji = when (co2Impact) {
                    "high" -> "🔴"
                    "medium" -> "🟡"
                    "low" -> "🟢"
                    else -> "⚪"
                }
                
                // Build tooltip with suggestion
                val tooltipText = buildString {
                    append("<html><body>")
                    append("<b>$icon Eco-Code Issue</b><br>")
                    append(message)
                    if (suggestion.isNotEmpty()) {
                        append("<br><br><b>💡 Suggestion:</b><br>")
                        append(suggestion)
                    }
                    append("<br><br><b>$impactEmoji CO₂ Impact:</b> $co2Impact")
                    append("</body></html>")
                }
                
                // Find the element at this line
                val offset = getOffsetForLine(file, lineNumber)
                if (offset >= 0 && offset < file.textLength) {
                    val elementAtLine = file.findElementAt(offset)
                    if (elementAtLine != null) {
                        holder.newAnnotation(severity, "$icon Eco-Code: $message")
                            .range(elementAtLine)
                            .tooltip(tooltipText)
                            .create()
                    }
                }
            } catch (e: Exception) {
                // Skip this issue if there's an error
            }
        }
    }
    
    private fun analyzeWithEcoCode(code: String): List<JsonObject> {
        return try {
            val pythonCmd = findPython()
            val scriptPath = getScriptPath("ecocode_analyzer.py")
            
            val process = ProcessBuilder(pythonCmd, scriptPath)
                .redirectErrorStream(true)
                .start()
            
            // Write code to stdin
            process.outputStream.bufferedWriter().use { writer ->
                writer.write(code)
                writer.flush()
            }
            
            // Read JSON output with timeout
            val output = process.inputStream.bufferedReader().use { it.readText() }
            val completed = process.waitFor(5, TimeUnit.SECONDS)
            
            if (!completed) {
                process.destroyForcibly()
                return fallbackAnalysis(code)
            }
            
            // Parse JSON result
            val result = gson.fromJson(output, JsonObject::class.java)
            val issuesArray = result?.getAsJsonArray("issues")
            
            if (issuesArray != null) {
                issuesArray.map { it.asJsonObject }.toList()
            } else {
                // Might be old format returning array directly
                try {
                    val jsonArray = gson.fromJson(output, Array<JsonObject>::class.java)
                    jsonArray.toList()
                } catch (e: Exception) {
                    fallbackAnalysis(code)
                }
            }
        } catch (e: Exception) {
            fallbackAnalysis(code)
        }
    }
    
    private fun fallbackAnalysis(code: String): List<JsonObject> {
        val issues = mutableListOf<JsonObject>()
        val lines = code.split("\n")
        val loopStack = mutableListOf<Pair<Int, Int>>() // (lineNumber, indent)
        
        for ((i, line) in lines.withIndex()) {
            val lineNumber = i + 1
            val trimmed = line.trim()
            val indent = line.length - line.trimStart().length
            
            // Skip empty lines and comments
            if (trimmed.isEmpty() || trimmed.startsWith("#")) continue
            
            // Update loop stack
            while (loopStack.isNotEmpty() && loopStack.last().second >= indent) {
                loopStack.removeAt(loopStack.size - 1)
            }
            
            // Check for loops
            if (trimmed.startsWith("for ") && "range(" in trimmed) {
                // Check for nested loops
                if (loopStack.isNotEmpty()) {
                    val issue = JsonObject()
                    issue.addProperty("line", lineNumber)
                    issue.addProperty("severity", "error")
                    issue.addProperty("type", "nested_loop")
                    issue.addProperty("message", "Nested loop detected - high CPU/energy usage")
                    issue.addProperty("suggestion", "Consider using NumPy or itertools.product()")
                    issue.addProperty("co2_impact", "high")
                    issues.add(issue)
                } else {
                    val issue = JsonObject()
                    issue.addProperty("line", lineNumber)
                    issue.addProperty("severity", "warning")
                    issue.addProperty("type", "inefficient_loop")
                    issue.addProperty("message", "Loop detected - consider list comprehension")
                    issue.addProperty("suggestion", "List comprehensions are often more efficient")
                    issue.addProperty("co2_impact", "medium")
                    issues.add(issue)
                }
                loopStack.add(Pair(lineNumber, indent))
            }
            
            // Check for while loops
            if (trimmed.startsWith("while ")) {
                loopStack.add(Pair(lineNumber, indent))
            }
            
            // File without context manager
            if ("open(" in line && "with " !in line && "def " !in line) {
                if (line.contains("=") && line.indexOf("=") < line.indexOf("open(")) {
                    val issue = JsonObject()
                    issue.addProperty("line", lineNumber)
                    issue.addProperty("severity", "warning")
                    issue.addProperty("type", "resource_leak")
                    issue.addProperty("message", "File opened without context manager")
                    issue.addProperty("suggestion", "Use 'with open(...) as f:' for safe resource handling")
                    issue.addProperty("co2_impact", "low")
                    issues.add(issue)
                }
            }
            
            // Wildcard imports
            if (trimmed.matches(Regex("from\\s+\\w+.*import\\s+\\*.*"))) {
                val issue = JsonObject()
                issue.addProperty("line", lineNumber)
                issue.addProperty("severity", "warning")
                issue.addProperty("type", "wildcard_import")
                issue.addProperty("message", "Wildcard import loads unnecessary modules")
                issue.addProperty("suggestion", "Import only specific items you need")
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
        // Skip leading whitespace to get to actual code
        val line = lines[lineNumber - 1]
        offset += line.length - line.trimStart().length
        return offset
    }
    
    private fun findPython(): String {
        val commands = listOf("python3", "python", "python.exe", "python3.exe")
        for (cmd in commands) {
            try {
                val process = ProcessBuilder(cmd, "--version").start()
                val completed = process.waitFor(2, TimeUnit.SECONDS)
                if (completed && process.exitValue() == 0) return cmd
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
                // URI might not be a file (e.g., inside JAR)
            }
        }
        
        // Extract from JAR to temp file
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
