import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    property real centerLat: 52.0910
    property real centerLon: 5.1225
    property int zoom: 14
    anchors.fill: parent

    // Store local points for computing car heading
    property var localPoints: []

    Rectangle {
        id: background
        anchors.fill: parent
        color: "black"

        Canvas {
            id: canvas
            anchors.fill: parent

            Image {
                id: carImg
                source: "../lib/icons/TopDownRedCar.png"
            }

            // Trigger repaint when canvas size changes
            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()

            Connections {
                target: root
                function onCenterLatChanged() { canvas.requestPaint() }
                function onCenterLonChanged() { canvas.requestPaint() }
                function onZoomChanged() { canvas.requestPaint() }
            }

            onPaint: {
                var ctx = getContext("2d")
                ctx.reset()
                ctx.clearRect(0, 0, width, height)

                carImg.visible = false

                var tileSize = 500
                var diameter = Math.min(width, height)
                var radius = diameter / 2
                var centerX = width / 2
                var centerY = height / 2

                // --- Clip to circular view ---
                ctx.save()
                ctx.beginPath()
                ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
                ctx.clip()

                // --- Compute map projection ---
                var latRad = root.centerLat * Math.PI / 180
                var n = Math.pow(2, root.zoom)
                var globalX = (root.centerLon + 180) / 360 * n * tileSize
                var globalY = ((1 - (Math.asinh(Math.tan(latRad)) / Math.PI)) / 2) * n * tileSize



                var viewWidth = width
                var viewHeight = height
                var minX = globalX - viewWidth / 2
                var minY = globalY - viewHeight / 2
                var maxX = globalX + viewWidth / 2
                var maxY = globalY + viewHeight / 2

                //addPoint(globalX, globalY)

                var tileXStart = Math.floor(minX / tileSize)
                var tileXEnd = Math.floor(maxX / tileSize)
                var tileYStart = Math.floor(minY / tileSize)
                var tileYEnd = Math.floor(maxY / tileSize)

                // --- Draw map tiles ---
                for (var tx = tileXStart; tx <= tileXEnd; tx++) {
                    for (var ty = tileYStart; ty <= tileYEnd; ty++) {
                        var px = tx * tileSize - minX
                        var py = ty * tileSize - minY

                        var filePath = "file:///C:/Users/jorer/OneDrive/Documenten/test/mapNL/" +
                                       root.zoom + "/" + tx + "/" + ty + ".png"

                        var img = Qt.createQmlObject('import QtQuick 2.15; Image {}', canvas)
                        img.source = filePath
                        img.width = tileSize
                        img.height = tileSize
                        img.visible = false

                        ctx.drawImage(img, px, py, tileSize, tileSize)
                        img.destroy() // cleanup temporary object
                    }
                }

                ctx.restore() // restore from circular clipping
                // Convert lon/lat to global pixel coordinates (Mercator)
                function latLonToPixels(lat, lon) {
                    var tileSize = 500
                    var n = Math.pow(2, root.zoom)
                    var x = (lon + 180) / 360 * n * tileSize
                    var latRad = lat * Math.PI / 180
                    var y = (1 - Math.asinh(Math.tan(latRad)) / Math.PI) / 2 * n * tileSize
                    return { x: x, y: y }
                }

                // Add current center as a point
                var pt = latLonToPixels(root.centerLat, root.centerLon)
                localPoints.push(pt)
                if (localPoints.length > 10) localPoints.shift()

                // Compute angle
                var angle = 0
                if (localPoints.length > 1) {
                    var prev = localPoints[localPoints.length - 2]
                    var curr = localPoints[localPoints.length - 1]

                    var dx = curr.x - prev.x
                    var dy = curr.y - prev.y
                    angle = Math.atan2(dy, dx)
                }

                if (carImg.status === Image.Ready) {
                    ctx.save()
                    ctx.translate(centerX, centerY)
                    ctx.rotate(angle+ Math.PI)
                    ctx.drawImage(carImg, -10, -10, 20, 20) // centered 20x20
                    ctx.restore()
                }
            }
        }
    }
}
