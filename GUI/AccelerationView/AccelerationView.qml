
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: clock
    property alias running: clockTimer.running
    property color clockColor: "white"

    // Adjust this to change size when embedded
    width: 300
    height: 300

    Canvas {
        id: clockCanvas
        anchors.fill: parent

        onPaint: {
            var ctx = getContext("2d")
            var w = width
            var h = height
            var cx = w / 2
            var cy = h / 2
            var radius = Math.min(w, h) / 2 - 10

            ctx.reset()
            ctx.clearRect(0, 0, w, h)

            // --- Metallic radial gradient border ---
            var gradient = ctx.createRadialGradient(cx, cy, radius * 0.5, cx, cy, radius)
            gradient.addColorStop(0, "#CCCCCC")
            gradient.addColorStop(0.5, "#888888")
            gradient.addColorStop(1, "#222222")

            ctx.strokeStyle = gradient
            ctx.lineWidth = 6
            ctx.beginPath()
            ctx.arc(cx, cy, radius, 0, 2 * Math.PI)
            ctx.stroke()

            // --- Tick Marks ---
            ctx.strokeStyle = clock.clockColor
            for (var i = 0; i < 60; i++) {
                var angle = i * Math.PI / 30
                var inner = radius - (i % 5 === 0 ? 20 : 10)
                var x1 = cx + Math.sin(angle) * inner
                var y1 = cy - Math.cos(angle) * inner
                var x2 = cx + Math.sin(angle) * radius
                var y2 = cy - Math.cos(angle) * radius
                ctx.lineWidth = i % 5 === 0 ? 3 : 1
                ctx.beginPath()
                ctx.moveTo(x1, y1)
                ctx.lineTo(x2, y2)
                ctx.stroke()
            }

            // --- Hour numbers ---
            ctx.fillStyle = clock.clockColor
            ctx.font = (radius / 8) + "px Arial"
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"
            for (var n = 1; n <= 12; n++) {
                var a = n * Math.PI / 6
                var x = cx + Math.sin(a) * (radius - 35)
                var y = cy - Math.cos(a) * (radius - 35)
                ctx.fillText(n.toString(), x, y)
            }

            // --- Time ---
            var now = new Date()
            var hour = now.getHours() % 12
            var minute = now.getMinutes()
            var second = now.getSeconds()

            var hourAng = (hour + minute / 60) * Math.PI / 6
            var minAng = (minute + second / 60) * Math.PI / 30

            // Hour hand
            ctx.strokeStyle = clock.clockColor
            ctx.lineWidth = 6
            ctx.beginPath()
            ctx.moveTo(cx, cy)
            ctx.lineTo(cx + Math.sin(hourAng) * radius * 0.5,
                       cy - Math.cos(hourAng) * radius * 0.5)
            ctx.stroke()

            // Minute hand
            ctx.lineWidth = 3
            ctx.beginPath()
            ctx.moveTo(cx, cy)
            ctx.lineTo(cx + Math.sin(minAng) * radius * 0.7,
                       cy - Math.cos(minAng) * radius * 0.7)
            ctx.stroke()

            // Center cap
            ctx.beginPath()
            ctx.arc(cx, cy, 10, 0, 2 * Math.PI)
            ctx.fillStyle = clock.clockColor
            ctx.fill()

            // Quartz text
            ctx.font = (radius / 12) + "px Arial"
            ctx.fillText("Quartz", cx, cy + radius * 0.45)
        }
    }

    Timer {
        id: clockTimer
        interval: 1000
        repeat: true
        running: true
        onTriggered: clockCanvas.requestPaint()
    }
}
