import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    anchors.fill: parent

    property real ax: 3
    property real ay: 2
    property real maxAcceleration: 5
    property int contourCount: 4   // number of concentric circles
    property int tickCount: 4      // number of ticks per axis
    property int labelOffset: 15   // distance from tick toward center
     property color textColor: "yellow"

    Rectangle {
        anchors.fill: parent
        color: "black"

        // Background disk
        Rectangle {
            anchors.centerIn: parent
            width: parent.width
            height: parent.height
            color: "black"
        }

        // Contour lines
        Repeater {
            model: contourCount
            Rectangle {
                width: disk.width * (index + 1) / contourCount
                height: disk.height * (index + 1) / contourCount
                anchors.centerIn: disk
                radius: width / 3
                color: "transparent"
                border.color: "#555"
                border.width: 1
            }
        }

        // Main disk
        Rectangle {
            id: disk
            width: parent.height/2
            height: parent.height/2
            anchors.centerIn: parent
            radius: parent.height/6
            border.color: textColor
            border.width: 2
            color: "transparent"
        }

        // X/Y axes
        Rectangle {
            width: disk.width
            height: 1
            color: "#888"
            anchors.horizontalCenter: disk.horizontalCenter
            anchors.verticalCenter: disk.verticalCenter
        }
        Rectangle {
            width: 1
            height: disk.height
            color: "#888"
            anchors.horizontalCenter: disk.horizontalCenter
            anchors.verticalCenter: disk.verticalCenter
        }

        // X-axis ticks and labels (skip 0)
        Repeater {
            model: tickCount * 2 + 1
            delegate: Item {
                property real tickValue: (index - tickCount) * maxAcceleration / tickCount
                visible: tickValue !== 0  // skip the center tick

                Rectangle {
                    width: 2
                    height: 8
                    color: "#aaa"
                    x: disk.x + disk.width/2 + tickValue / maxAcceleration * (disk.width/2) - width/2
                    y: disk.y + disk.height/2 - height/2
                }

                Text {
                    text: tickValue.toFixed(0)
                    color: textColor
                    font.pixelSize: 15
                    x: disk.x + disk.width/2 + tickValue / maxAcceleration * (disk.width/2) - width/2 + (tickValue > 0 ? -labelOffset : labelOffset)
                    y: disk.y + disk.height/2 + 10
                }
            }
        }

        // Y-axis ticks and labels (skip 0)
        Repeater {
            model: tickCount * 2 + 1
            delegate: Item {
                property real tickValue: (index - tickCount) * maxAcceleration / tickCount
                visible: tickValue !== 0  // skip the center tick

                Rectangle {
                    width: 8
                    height: 2
                    color: "#aaa"
                    x: disk.x + disk.width/2 - width/2
                    y: disk.y + disk.height/2 - tickValue / maxAcceleration * (disk.height/2) - height/2
                }

                Text {
                    text: tickValue.toFixed(0)
                    color: textColor
                    font.pixelSize: 15
                    x: disk.x + disk.width/2 - 30
                    y: disk.y + disk.height/2 - tickValue / maxAcceleration * (disk.height/2) - height/2 + (tickValue > 0 ? labelOffset : -labelOffset)
                }
            }
        }

        // Acceleration point
        Rectangle {
            width: 16
            height: 16
            radius: 5
            color: "red"
            x: disk.x + disk.width/2 + (ax / maxAcceleration) * (disk.width/2) - width/2
            y: disk.y + disk.height/2 - (ay / maxAcceleration) * (disk.height/2) - height/2
            layer.enabled: true
        }
    }
}
