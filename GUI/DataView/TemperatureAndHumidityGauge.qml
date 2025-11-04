import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: gauge
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

    width: 280
    height: 280

    Canvas {
        id: canvas
        anchors.fill: parent
        antialiasing: true

        onPaint: {
            var ctx = getContext("2d");
            var w = width;
            var h = height;
            var cx = w / 2;
            var cy = h / 2;
            var radius = Math.min(w, h) / 2 * 0.9;

            // clear canvas with black
            ctx.reset();
            ctx.fillStyle = "black";
            ctx.fillRect(0, 0, w, h);

            // rim
            ctx.beginPath();
            ctx.arc(cx, cy, radius, 0, 2*Math.PI);
            ctx.fillStyle = rimColor;
            ctx.fill();

            // inner dial
            var dialRadius = radius * 0.95;
            ctx.beginPath();
            ctx.arc(cx, cy, dialRadius, 0, 2*Math.PI);
            ctx.fillStyle = "#111";
            ctx.fill();

            // ticks
            ctx.strokeStyle = dialColor;
            ctx.fillStyle = dialColor;
            ctx.lineWidth = radius * 0.015;  // relative line width
            ctx.font = (dialRadius * 0.15) + "px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            var minTemp = minTemperature;
            var maxTemp = maxTemperature;
            var range = maxTemp - minTemp;
            var majorTicks = 8;

            for (var i=0; i<=majorTicks; i++) {
                var tickValue = minTemp + i*(range/majorTicks);
                var normalized = (tickValue - minTemp)/range;
                var angle = Math.PI*1.2*normalized + Math.PI*0.9;
                var len = (i%2 === 0) ? dialRadius*0.12 : dialRadius*0.07;
                var x1 = cx + Math.cos(angle)*(dialRadius-len);
                var y1 = cy + Math.sin(angle)*(dialRadius-len);
                var x2 = cx + Math.cos(angle)*dialRadius;
                var y2 = cy + Math.sin(angle)*dialRadius;
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();

                if (i%2 === 0) {
                    var lx = cx + Math.cos(angle)*(dialRadius-len-0.12*dialRadius);
                    var ly = cy + Math.sin(angle)*(dialRadius-len-0.12*dialRadius);
                    ctx.fillText(tickValue.toFixed(0), lx, ly);
                }
            }

            // humidity arc
            if (showHumidity) {
                var humNorm = (humidity - minHumidity)/(maxHumidity - minHumidity);
                humNorm = Math.min(Math.max(humNorm, 0), 1);
                var startAngle = Math.PI*0.9;
                var endAngle = Math.PI*0.9 + Math.PI*1.2*humNorm;

                // gradient from blue to red
                var grad = ctx.createLinearGradient(cx-dialRadius, cy, cx+dialRadius, cy);
                grad.addColorStop(0, "blue");
                grad.addColorStop(1, "red");
                ctx.strokeStyle = grad;
                ctx.lineWidth = radius*0.05;
                ctx.beginPath();
                ctx.arc(cx, cy, dialRadius*0.5, startAngle, endAngle);
                ctx.stroke();

                // humidity text
                ctx.fillStyle = dialColor;
                ctx.font = (dialRadius*0.20) + "px Arial";
                ctx.fillText(humidity.toFixed(0) + " %", cx, cy + dialRadius*0.40);
            }

            // temperature needle
            var valNorm = (temperature - minTemp)/range;
            valNorm = Math.min(Math.max(valNorm, 0), 1);
            var needleAngle = Math.PI*1.2*valNorm + Math.PI*0.9;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            var nx = cx + Math.cos(needleAngle)*dialRadius*0.8;
            var ny = cy + Math.sin(needleAngle)*dialRadius*0.8;
            ctx.lineWidth = radius*0.025;
            ctx.strokeStyle = needleColor;
            ctx.lineTo(nx, ny);
            ctx.stroke();

            // center cap
            ctx.beginPath();
            ctx.arc(cx, cy, radius*0.06, 0, 2*Math.PI);
            ctx.fillStyle = needleColor;
            ctx.fill();

            // value text
            ctx.fillStyle = dialColor;
            ctx.font = (dialRadius*0.25) + "px Arial";
            ctx.fillText(temperature.toFixed(1) + " °C", cx, cy + dialRadius*0.7);
        }
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: canvas.requestPaint()
    }
}
