package com.hackathon.eco

import com.intellij.openapi.util.ScalableIcon
import com.intellij.ui.JBColor
import com.intellij.ui.scale.JBUIScale
import java.awt.*
import java.awt.geom.Path2D
import java.awt.image.BufferedImage
import javax.swing.Icon

/**
 * Provides dynamic colored icons for the Green Coding Assistant.
 * The icon color changes gradually based on the eco score:
 * - High (80-100): Green
 * - Medium (50-79): Yellow/Orange gradient
 * - Low (0-49): Red
 */
object EcoIconProvider {

    private const val ICON_SIZE = 13

    /**
     * Get a colored leaf icon based on the eco score.
     * Colors transition smoothly between red, yellow, and green.
     */
    fun getColoredIcon(score: Int): Icon {
        val color = getGradientColor(score)
        return EcoLeafIcon(color, ICON_SIZE)
    }

    /**
     * Get a gray icon for when no file is analyzed.
     */
    fun getGrayIcon(): Icon {
        return EcoLeafIcon(JBColor.GRAY, ICON_SIZE)
    }

    /**
     * Calculate gradient color based on score.
     * 0-50: Red to Yellow
     * 50-100: Yellow to Green
     */
    private fun getGradientColor(score: Int): Color {
        val clampedScore = score.coerceIn(0, 100)
        
        return when {
            clampedScore <= 50 -> {
                // Red (244, 67, 54) to Yellow (255, 193, 7)
                val ratio = clampedScore / 50.0f
                Color(
                    lerp(244, 255, ratio),
                    lerp(67, 193, ratio),
                    lerp(54, 7, ratio)
                )
            }
            else -> {
                // Yellow (255, 193, 7) to Green (76, 175, 80)
                val ratio = (clampedScore - 50) / 50.0f
                Color(
                    lerp(255, 76, ratio),
                    lerp(193, 175, ratio),
                    lerp(7, 80, ratio)
                )
            }
        }
    }

    private fun lerp(start: Int, end: Int, ratio: Float): Int {
        return (start + (end - start) * ratio).toInt().coerceIn(0, 255)
    }

    /**
     * Create icons for different states - can be used for light/dark themes.
     */
    fun createScoreBasedIcons(): Map<String, Icon> {
        return mapOf(
            "excellent" to getColoredIcon(100),
            "good" to getColoredIcon(75),
            "warning" to getColoredIcon(50),
            "poor" to getColoredIcon(25),
            "gray" to getGrayIcon()
        )
    }
}

/**
 * A scalable leaf icon that implements IntelliJ's ScalableIcon interface.
 * This ensures compatibility with IntelliJ's tool window icon system.
 */
class EcoLeafIcon(
    private val color: Color,
    private val baseSize: Int
) : Icon, ScalableIcon {

    private var scale: Float = 1.0f

    override fun getIconWidth(): Int = (baseSize * scale).toInt()
    
    override fun getIconHeight(): Int = (baseSize * scale).toInt()

    override fun getScale(): Float = scale

    override fun scale(scaleFactor: Float): Icon {
        val scaled = EcoLeafIcon(color, baseSize)
        scaled.scale = scaleFactor
        return scaled
    }

    override fun paintIcon(c: Component?, g: Graphics, x: Int, y: Int) {
        val g2d = g.create() as Graphics2D
        
        try {
            // Enable anti-aliasing
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
            g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY)
            g2d.setRenderingHint(RenderingHints.KEY_STROKE_CONTROL, RenderingHints.VALUE_STROKE_PURE)
            
            // Translate to icon position
            g2d.translate(x, y)
            
            // Scale if needed
            if (scale != 1.0f) {
                g2d.scale(scale.toDouble(), scale.toDouble())
            }
            
            // Draw leaf shape
            val leaf = createLeafShape(baseSize)
            
            // Fill with gradient
            val gradient = GradientPaint(
                0f, 0f, color.brighter(),
                baseSize.toFloat(), baseSize.toFloat(), color.darker()
            )
            g2d.paint = gradient
            g2d.fill(leaf)
            
            // Draw outline
            g2d.color = color.darker().darker()
            g2d.stroke = BasicStroke(0.5f)
            g2d.draw(leaf)
            
            // Draw leaf vein
            g2d.color = Color(color.red, color.green, color.blue, 100)
            g2d.stroke = BasicStroke(0.8f)
            g2d.drawLine(baseSize / 2, baseSize - 2, baseSize / 2, 3)
            
        } finally {
            g2d.dispose()
        }
    }

    /**
     * Create a leaf shape path.
     */
    private fun createLeafShape(size: Int): Shape {
        val path = Path2D.Double()
        val cx = size / 2.0
        val cy = size / 2.0
        
        // Leaf shape using bezier curves
        path.moveTo(cx, size - 1.5)  // Bottom point (stem)
        
        // Right side curve
        path.curveTo(
            cx + size * 0.4, cy + size * 0.1,    // Control point 1
            cx + size * 0.35, cy - size * 0.3,   // Control point 2
            cx, 1.5                               // Top point
        )
        
        // Left side curve
        path.curveTo(
            cx - size * 0.35, cy - size * 0.3,   // Control point 1
            cx - size * 0.4, cy + size * 0.1,    // Control point 2
            cx, size - 1.5                        // Back to bottom
        )
        
        path.closePath()
        return path
    }
}
