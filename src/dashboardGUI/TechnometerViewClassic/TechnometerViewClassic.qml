import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    width: parent ? parent.width : 800
    height: parent ? parent.height : 800

    property real rpm: 0
    property real maxRpm: 7000
    property real redlineRpm: 6000

    property real startingAngle: -225 // left-most tick
    property real endingAngle: 45    // right-most tick

    property color textColor: "white"
    property color redlineColor: "#ff3b3b"

    // Animated needle position (0..1)
    property real needlePos: 0
    readonly property real redlineNorm: redlineRpm / maxRpm

    // Animate needlePos whenever it changes
    Behavior on needlePos {
        SpringAnimation {
            spring: 3
            damping: 0.3
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "black"
    }

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
            const radius = Math.min(w, h) * 0.5

            const subticks = 4

            // --- Background ---
            ctx.reset()
            ctx.fillStyle = "black"
            ctx.fillRect(0, 0, w, h)

            // --- Dial Background ---
            const dialRadius = radius * 0.95
            ctx.beginPath()
            ctx.arc(cx, cy, dialRadius, 0, 2 * Math.PI)
            ctx.fillStyle = "black"
            ctx.fill()

            // --- Major Ticks & Labels ---
            const majorTicks = 7
            ctx.strokeStyle = textColor
            ctx.fillStyle = textColor
            ctx.lineWidth = radius * 0.015
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"
            ctx.font = `${dialRadius * 0.1}px Arial`

            for (let i = 0; i <= majorTicks; i++) {
                const tickNorm = i / majorTicks
                const angle = (startingAngle + (endingAngle - startingAngle) * tickNorm) * Math.PI / 180

                const tickLength = dialRadius * 0.12
                const x1 = cx + Math.cos(angle) * (dialRadius - tickLength)
                const y1 = cy + Math.sin(angle) * (dialRadius - tickLength)
                const x2 = cx + Math.cos(angle) * dialRadius
                const y2 = cy + Math.sin(angle) * dialRadius

                // Major tick
                ctx.beginPath()
                ctx.moveTo(x1, y1)
                ctx.lineTo(x2, y2)
                ctx.stroke()

                // Label (10, 20, 30, ...)
                const labelValue = i * 10
                const lx = cx + Math.cos(angle) * (dialRadius - tickLength - dialRadius * 0.15)
                const ly = cy + Math.sin(angle) * (dialRadius - tickLength - dialRadius * 0.15)
                ctx.fillStyle = textColor
                ctx.fillText(labelValue, lx, ly)

                // Subticks
                if (i < majorTicks) {
                    for (let s = 1; s < subticks; s++) {
                        const subNorm = (i + s / subticks) / majorTicks
                        const subAngle = (startingAngle + (endingAngle - startingAngle) * subNorm) * Math.PI / 180
                        const subLength = dialRadius * 0.07
                        const sx1 = cx + Math.cos(subAngle) * (dialRadius - subLength)
                        const sy1 = cy + Math.sin(subAngle) * (dialRadius - subLength)
                        const sx2 = cx + Math.cos(subAngle) * dialRadius
                        const sy2 = cy + Math.sin(subAngle) * dialRadius
                        ctx.beginPath()
                        ctx.moveTo(sx1, sy1)
                        ctx.lineTo(sx2, sy2)
                        ctx.lineWidth = radius * 0.01
                        ctx.stroke()
                    }
                }
            }

            // --- Redline Arc ---
            const redlineStartAngle = startingAngle + (endingAngle - startingAngle) * redlineNorm
            ctx.beginPath()
            ctx.lineWidth = dialRadius * 0.05
            ctx.strokeStyle = redlineColor
            ctx.arc(cx, cy, dialRadius * 0.85, redlineStartAngle * Math.PI / 180, endingAngle * Math.PI / 180)
            ctx.stroke()

            // --- Needle Glow ---
            if (needlePos > redlineNorm) {
                ctx.beginPath()
                ctx.lineWidth = dialRadius * 0.05
                ctx.strokeStyle = `rgba(255,59,59,${(needlePos - redlineNorm) * 2})`
                const needleGlowAngle = startingAngle + (endingAngle - startingAngle) * needlePos
                const nxGlow = cx + Math.cos(needleGlowAngle * Math.PI / 180) * dialRadius * 0.8
                const nyGlow = cy + Math.sin(needleGlowAngle * Math.PI / 180) * dialRadius * 0.8
                ctx.moveTo(cx, cy)
                ctx.lineTo(nxGlow, nyGlow)
                ctx.stroke()
            }

            // --- Needle ---
            const needleAngle = startingAngle + (endingAngle - startingAngle) * needlePos
            const nx = cx + Math.cos(needleAngle * Math.PI / 180) * dialRadius * 0.8
            const ny = cy + Math.sin(needleAngle * Math.PI / 180) * dialRadius * 0.8
            ctx.beginPath()
            ctx.moveTo(cx, cy)
            ctx.lineTo(nx, ny)
            ctx.strokeStyle = textColor
            ctx.lineWidth = radius * 0.01
            ctx.stroke()

            // --- Center Cap ---
            ctx.beginPath()
            ctx.arc(cx, cy, radius * 0.06, 0, 2 * Math.PI)
            ctx.fillStyle = "black"
            ctx.fill()

            // --- Text "tr/min x100" ---
            ctx.fillStyle = textColor
            ctx.font = `${dialRadius * 0.1}px Arial`
            ctx.fillText("tr/min x100", cx, cy - dialRadius * 0.5)
        }
    }

    onRpmChanged: needlePos = Math.min(rpm / maxRpm, 1)
    onTextColorChanged: canvas.requestPaint()
    onNeedlePosChanged: canvas.requestPaint()
}
