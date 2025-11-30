package com.hackathon.eco

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.intellij.util.messages.Topic

/**
 * Service for managing and broadcasting eco scores across the plugin.
 * Allows the carbon tracking results to update the tool window score.
 */
@Service(Service.Level.PROJECT)
class EcoScoreService(private val project: Project) {

    companion object {
        @JvmStatic
        fun getInstance(project: Project): EcoScoreService {
            return project.getService(EcoScoreService::class.java)
        }

        // Topic for score update notifications
        val SCORE_UPDATED_TOPIC = Topic.create("EcoScoreUpdated", ScoreUpdateListener::class.java)
    }

    private var lastEmissionsGrams: Double = 0.0
    private var lastDurationSeconds: Double = 0.0
    private var lastRuntimeScore: Int? = null

    /**
     * Calculate and broadcast a runtime score based on actual carbon emissions.
     * 
     * Scoring logic:
     * - Base score starts at 100
     * - Deductions based on emissions per second of execution
     * - Very efficient code (< 0.0001g/s) keeps high score
     * - Heavy code (> 0.01g/s) gets low score
     */
    fun updateFromCarbonTracking(emissionsGrams: Double, durationSeconds: Double, energyKwh: Double) {
        lastEmissionsGrams = emissionsGrams
        lastDurationSeconds = durationSeconds

        // Calculate emissions rate (grams per second)
        val emissionsRate = if (durationSeconds > 0) {
            emissionsGrams / durationSeconds
        } else {
            emissionsGrams
        }

        // Calculate score based on emissions rate
        // Scale: very low emissions = 100, very high = 0
        val runtimeScore = when {
            emissionsRate <= 0.00001 -> 100  // Extremely efficient
            emissionsRate <= 0.00005 -> 95
            emissionsRate <= 0.0001 -> 90
            emissionsRate <= 0.0005 -> 85
            emissionsRate <= 0.001 -> 75
            emissionsRate <= 0.005 -> 65
            emissionsRate <= 0.01 -> 55
            emissionsRate <= 0.05 -> 45
            emissionsRate <= 0.1 -> 35
            emissionsRate <= 0.5 -> 25
            emissionsRate <= 1.0 -> 15
            else -> 5  // Very high emissions
        }

        lastRuntimeScore = runtimeScore

        // Broadcast the update
        project.messageBus.syncPublisher(SCORE_UPDATED_TOPIC).onScoreUpdated(
            runtimeScore,
            emissionsGrams,
            durationSeconds,
            energyKwh
        )
    }

    fun getLastRuntimeScore(): Int? = lastRuntimeScore
    fun getLastEmissions(): Double = lastEmissionsGrams
    fun getLastDuration(): Double = lastDurationSeconds

    /**
     * Listener interface for score updates.
     */
    interface ScoreUpdateListener {
        fun onScoreUpdated(score: Int, emissionsGrams: Double, durationSeconds: Double, energyKwh: Double)
    }
}

