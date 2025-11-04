import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    property real centerLat: 52.0910
    property real centerLon: 5.1225
    property int zoom: 14
    anchors.fill: parent

    Rectangle {
        id: background
        anchors.fill: parent
        color: "black"

        Canvas {
            id: canvas
            anchors.fill: parent

            onPaint: {
                var ctx = getContext("2d")
                ctx.reset()
                ctx.clearRect(0, 0, width, height)

                var tileSize = 256

                var diameter = Math.min(width, height)
                var radius = diameter / 2
                var centerX = width / 2
                var centerY = height / 2

                // --- Clip to circle ---
                ctx.save()
                ctx.beginPath()
                ctx.arc(centerX, centerY, radius, 0, 2*Math.PI)
                ctx.clip()

                // --- Compute global pixel coordinates ---
                var latRad = centerLat * Math.PI / 180


                var n = Math.pow(2, zoom)
                var globalX = (centerLon + 180) / 360 * n * tileSize
                var globalY = ((1 - (Math.asinh(Math.tan(latRad)) / Math.PI)) / 2) * n * tileSize

                var viewWidth = width;   // use canvas width
                var viewHeight = height; // use canvas height
                var minX = globalX - viewWidth/2;
                var minY = globalY - viewHeight/2;
                var maxX = globalX + viewWidth/2;
                var maxY = globalY + viewHeight/2;

                var tileXStart = Math.floor(minX / tileSize)
                var tileXEnd = Math.floor(maxX / tileSize)
                var tileYStart = Math.floor(minY / tileSize)
                var tileYEnd = Math.floor(maxY / tileSize)

                for (var tx = tileXStart; tx <= tileXEnd; tx++) {
                    for (var ty = tileYStart; ty <= tileYEnd; ty++) {
                        var px = tx * tileSize - minX
                        var py = ty * tileSize - minY

                        var filePath = "FILE:///C:/Users/jorer/OneDrive/Documenten/test/mapNL/" + zoom + "/" + tx + "/" + ty + ".png"
                        var img = Qt.createQmlObject('import QtQuick 2.15; Image {}', canvas)
                        img.source = filePath
                        img.width = tileSize
                        img.height = tileSize
                        // To make sure wrong image is not visible.
                        img.visible = false

                        ctx.drawImage(img, px, py, tileSize, tileSize)
                    }
                }

                ctx.restore()

                // Optional: draw a red dot at center
                ctx.fillStyle = "red"
                ctx.beginPath()
                ctx.arc(centerX, centerY, 4, 0, 2*Math.PI)
                ctx.fill()
            }

            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()
        }
    }
}
