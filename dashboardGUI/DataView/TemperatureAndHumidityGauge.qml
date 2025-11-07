import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: gauge
    width: 280
    height: 280

    // === Public Properties ===
    property real temperature: 20
    property real minTemperature: -20
    property real maxTemperature: 60
    property real humidity: 80
    property real minHumidity: 0
    property real maxHumidity: 100
    property bool showHumidity: true

    property color dialColor: "white"
    property color needleColor: "#00AEEF"
    property color rimColor: "#444"

    // === Internal Constants ===
    readonly property int majorTicks: 8

    Canvas {
        id: canvas
        anchors.fill: parent
        antialiasing: true
        renderTarget: Canvas.FramebufferObject
        renderStrategy: Canvas.Threaded

        onPaint: {
            const ctx = getContext("2d")
            const w = width
            const h = height
            const cx = w / 2
            const cy = h / 2
            const radius = Math.min(w, h) * 0.45

            ctx.reset()
            ctx.fillStyle = "black"
            ctx.fillRect(0, 0, w, h)

            // --- Rim ---
            ctx.beginPath()
            ctx.arc(cx, cy, radius, 0, 2 * Math.PI)
            ctx.fillStyle = rimColor
            ctx.fill()

            // --- Dial background ---
            const dialRadius = radius * 0.95
            ctx.beginPath()
            ctx.arc(cx, cy, dialRadius, 0, 2 * Math.PI)
            ctx.fillStyle = "#111"
            ctx.fill()

            // --- Draw tick marks + labels ---
            const range = maxTemperature - minTemperature
            ctx.strokeStyle = dialColor
            ctx.fillStyle = dialColor
            ctx.lineWidth = radius * 0.015
            ctx.font = `${dialRadius * 0.15}px Arial`
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"

            for (let i = 0; i <= majorTicks; i++) {
                const tickValue = minTemperature + i * (range / majorTicks)
                const normalized = i / majorTicks
                const angle = Math.PI * (0.9 + 1.2 * normalized)
                const isMajor = i % 2 === 0
                const len = dialRadius * (isMajor ? 0.12 : 0.07)

                const x1 = cx + Math.cos(angle) * (dialRadius - len)
                const y1 = cy + Math.sin(angle) * (dialRadius - len)
                const x2 = cx + Math.cos(angle) * dialRadius
                const y2 = cy + Math.sin(angle) * dialRadius

                ctx.beginPath()
                ctx.moveTo(x1, y1)
                ctx.lineTo(x2, y2)
                ctx.stroke()

                if (isMajor) {
                    const lx = cx + Math.cos(angle) * (dialRadius - len - dialRadius * 0.15)
                    const ly = cy + Math.sin(angle) * (dialRadius - len - dialRadius * 0.15)
                    ctx.fillText(tickValue.toFixed(0), lx, ly)
                }
            }

            // --- Optional Humidity Arc ---
            if (showHumidity) {
                const humNorm = Math.min(Math.max((humidity - minHumidity) / (maxHumidity - minHumidity), 0), 1)
                const startAngle = Math.PI * 0.9
                const endAngle = startAngle + Math.PI * 1.2 * humNorm

                const grad = ctx.createLinearGradient(cx - dialRadius, cy, cx + dialRadius, cy)
                grad.addColorStop(0, "blue")
                grad.addColorStop(1, "red")

                ctx.strokeStyle = grad
                ctx.lineWidth = radius * 0.05
                ctx.beginPath()
                ctx.arc(cx, cy, dialRadius * 0.5, startAngle, endAngle)
                ctx.stroke()

                ctx.fillStyle = dialColor
                ctx.font = `${dialRadius * 0.20}px Arial`
                ctx.fillText(`${humidity.toFixed(0)} %`, cx, cy + dialRadius * 0.40)
            }

            // --- Temperature Needle ---
            const tNorm = Math.min(Math.max((temperature - minTemperature) / range, 0), 1)
            const needleAngle = Math.PI * (0.9 + 1.2 * tNorm)
            const nx = cx + Math.cos(needleAngle) * dialRadius * 0.8
            const ny = cy + Math.sin(needleAngle) * dialRadius * 0.8

            ctx.beginPath()
            ctx.moveTo(cx, cy)
            ctx.lineTo(nx, ny)
            ctx.strokeStyle = needleColor
            ctx.lineWidth = radius * 0.025
            ctx.stroke()

            // --- Center Cap ---
            ctx.beginPath()
            ctx.arc(cx, cy, radius * 0.06, 0, 2 * Math.PI)
            ctx.fillStyle = needleColor
            ctx.fill()

            // --- Temperature Text ---
            ctx.fillStyle = dialColor
            ctx.font = `${dialRadius * 0.25}px Arial`
            ctx.fillText(`${temperature.toFixed(1)} °C`, cx, cy + dialRadius * 0.7)
        }
    }

    // Smooth update only when properties change (not constant repaint)
    onTemperatureChanged: canvas.requestPaint()
    onHumidityChanged: canvas.requestPaint()
}
