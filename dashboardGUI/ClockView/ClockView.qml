import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: clock
    property alias running: clockTimer.running
    property color clockColor: "white"
    property color rimColor: "black"
    property color faceColor: "black"

    // GPS time string in "HH:MM" format
    property string gpsTime: "00:00"

    width: 300
    height: 300

    Canvas {
        id: clockCanvas
        anchors.fill: parent
        antialiasing: true

        onPaint: {
            var ctx = getContext("2d")
            var w = width
            var h = height
            var cx = w / 2
            var cy = h / 2
            var radius = Math.min(w, h) / 2
            var faceRadius = radius * 0.99

            ctx.clearRect(0, 0, w, h)

            // Background
            ctx.fillStyle = "black"
            ctx.fillRect(0, 0, w, h)

            // Outer rim
            ctx.beginPath()
            ctx.arc(cx, cy, radius, 0, 2 * Math.PI)
            ctx.fillStyle = rimColor
            ctx.fill()

            // Inner face
            ctx.beginPath()
            ctx.arc(cx, cy, faceRadius, 0, 2 * Math.PI)
            ctx.fillStyle = faceColor
            ctx.fill()

            // Ticks
            ctx.strokeStyle = clockColor
            for (var i = 0; i < 60; i++) {
                var angle = i * Math.PI / 30
                var len = (i % 5 === 0 ? 20 : 10)
                var x1 = cx + Math.sin(angle) * (faceRadius - len)
                var y1 = cy - Math.cos(angle) * (faceRadius - len)
                var x2 = cx + Math.sin(angle) * faceRadius
                var y2 = cy - Math.cos(angle) * faceRadius
                ctx.lineWidth = i % 5 === 0 ? 3 : 1
                ctx.beginPath()
                ctx.moveTo(x1, y1)
                ctx.lineTo(x2, y2)
                ctx.stroke()
            }

            // Hour numbers
            ctx.fillStyle = clockColor
            ctx.font = (radius / 8) + "px Arial"
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"
            for (var n = 1; n <= 12; n++) {
                var a = n * Math.PI / 6
                var x = cx + Math.sin(a) * (faceRadius - 50)
                var y = cy - Math.cos(a) * (faceRadius - 50)
                ctx.fillText(n.toString(), x, y)
            }

            // --- Parse GPS time ---
            var parts = gpsTime.split(":")
            var hour = parseInt(parts[0]) % 12
            var minute = parseInt(parts[1])
            var second = 0  // no seconds info in GPS string

            var hourAng = (hour + minute / 60) * Math.PI / 6
            var minAng = (minute + second / 60) * Math.PI / 30

            // Hour hand
            ctx.strokeStyle = clockColor
            ctx.lineWidth = 6
            ctx.beginPath()
            ctx.moveTo(cx, cy)
            ctx.lineTo(cx + Math.sin(hourAng) * faceRadius * 0.5,
                       cy - Math.cos(hourAng) * faceRadius * 0.5)
            ctx.stroke()

            // Center cap
            ctx.beginPath()
            ctx.arc(cx, cy, radius / 14, 0, 2 * Math.PI)
            ctx.fillStyle = rimColor
            ctx.fill()

            // Minute hand
            ctx.lineWidth = 4
            ctx.beginPath()
            ctx.moveTo(cx, cy)
            ctx.lineTo(cx + Math.sin(minAng) * faceRadius * 0.7,
                       cy - Math.cos(minAng) * faceRadius * 0.7)
            ctx.stroke()

            // "Quartz" label
            ctx.font = (radius / 12) + "px Arial"
            ctx.fillStyle = clockColor
            ctx.fillText("Quartz", cx, cy + faceRadius * 0.45)
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
