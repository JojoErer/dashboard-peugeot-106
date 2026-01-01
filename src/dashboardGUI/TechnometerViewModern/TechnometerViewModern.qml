import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    width: parent ? parent.width : 800
    height: parent ? parent.height : 800

    property real rpm: 0
    property real maxRpm: 7000
    property real redlineRpm: 6000

    property color textColor: "white"

    property color bgColor: "black"
    property color greenColor: "#00ff66"
    property color blueColor: "#00c8ff"
    property color redColor: "#ff3b3b"
    property color inactiveColor: "#222"

    readonly property real rpmNorm: Math.min(rpm / maxRpm, 1)
    readonly property real redlineNorm: redlineRpm / maxRpm

    property var shiftLights: [
        0.3, 0.4, 0.5,   // green
        0.6, 0.7,         // blue
        0.8, 0.90, 0.95    // red
    ]

    // Background disk
    Rectangle {
        anchors.fill: parent
        color: "black"
    }

    Canvas {
        id: canvas
        antialiasing: true
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.8
        height: Math.min(parent.width, parent.height) * 0.5

        onPaint: {
            const ctx = getContext("2d")
            const w = width
            const h = height
            ctx.reset()
            ctx.clearRect(0, 0, w, h)

            // Background
            ctx.fillStyle = bgColor
            ctx.fillRect(0, 0, w, h)

            // Horizontal bar
            const padding = w * 0.05
            const barHeight = h * 0.12
            const barWidth = w - padding * 2
            const barX = padding
            const barY = h / 2 - barHeight / 2

            // Background bar
            ctx.fillStyle = inactiveColor
            ctx.fillRect(barX, barY, barWidth, barHeight)

            // Gradient for active bar
            const gradient = ctx.createLinearGradient(barX, 0, barX + barWidth, 0)
            gradient.addColorStop(0.0, greenColor)
            gradient.addColorStop(0.6, greenColor)
            gradient.addColorStop(0.6, blueColor)
            gradient.addColorStop(0.8, blueColor)
            gradient.addColorStop(0.8, redColor)
            gradient.addColorStop(1.0, redColor)

            const fillWidth = barWidth * rpmNorm
            ctx.fillStyle = gradient
            ctx.fillRect(barX, barY, fillWidth, barHeight)

            // Shift lights (LEDs)
            const lightCount = shiftLights.length
            const lightSize = barHeight * 0.6
            const lightGap = lightSize * 0.4
            const totalLightsWidth = lightCount * lightSize + (lightCount - 1) * lightGap

            let lx = w / 2 - totalLightsWidth / 2
            const ly = barY - lightSize * 1.5

            for (let i = 0; i < lightCount; i++) {
                let color = inactiveColor
                if (rpmNorm >= shiftLights[i]) {
                    if (i < 3) color = greenColor
                    else if (i < 5) color = blueColor
                    else color = redColor
                }

                // LED glow effect
                ctx.save()
                ctx.shadowBlur = lightSize * 0.8
                ctx.shadowColor = color

                const ledGradient = ctx.createRadialGradient(
                    lx + lightSize/2, ly, lightSize*0.1,
                    lx + lightSize/2, ly, lightSize/2
                )
                ledGradient.addColorStop(0, color)
                ledGradient.addColorStop(0.7, color)
                ledGradient.addColorStop(1, "#111")

                ctx.beginPath()
                ctx.arc(lx + lightSize / 2, ly, lightSize / 2, 0, 2 * Math.PI)
                ctx.fillStyle = ledGradient
                ctx.fill()
                ctx.restore()

                lx += lightSize + lightGap
            }

            // RPM text
            ctx.fillStyle = textColor
            ctx.font = `${barHeight * 1}px Arial`
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"
            ctx.fillText(Math.round(rpm) + " RPM", w / 2, barY + barHeight + barHeight)
        }
    }

    onRpmChanged: canvas.requestPaint()
}