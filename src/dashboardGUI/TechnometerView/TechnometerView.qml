import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    width: 400
    height: 400

    property real rpm: 0
    property real maxRpm: 8000
    property real redlineRpm: 6500

    property color textColor: "white"
    property color redlineColor: "#ff3b3b"

    readonly property real rpmNorm: Math.min(rpm / maxRpm, 1)
    readonly property real redlineNorm: redlineRpm / maxRpm

    // ====== BACKGROUND ======
    Rectangle {
        anchors.fill: parent
        color: "black"
    }

    // ====== DIAL CONTAINER ======
    Item {
        id: dial
        width: Math.min(parent.width, parent.height) * 0.8
        height: width
        anchors.centerIn: parent

        // Outer ring
        Rectangle {
            anchors.fill: parent
            radius: width / 2
            border.color: textColor
            border.width: 4
            color: "transparent"
        }

        // Redline arc
        Repeater {
            model: 30
            Rectangle {
                width: 6
                height: 18
                radius: 3
                anchors.centerIn: parent
                property real t: index / (model - 1)
                visible: t >= root.redlineNorm
                color: root.redlineColor
                transform: [
                    Rotation {
                        angle: -135 + t * 270
                        origin.x: dial.width/2
                        origin.y: dial.height/2
                    },
                    Translate { y: -dial.height/2 + 12 }
                ]
            }
        }

        // Major ticks
        Repeater {
            model: 9
            Rectangle {
                width: 4
                height: 22
                color: textColor
                anchors.centerIn: parent
                transform: [
                    Rotation {
                        angle: -135 + index * 270 / 8
                        origin.x: dial.width/2
                        origin.y: dial.height/2
                    },
                    Translate { y: -dial.height/2 + 10 }
                ]
            }
        }

        // Labels
        Repeater {
            model: 9
            Text {
                text: index
                font.pointSize: 14
                font.bold: index >= 7
                color: index * 1000 >= root.redlineRpm ? root.redlineColor : textColor

                x: dial.width/2 - width/2
                y: dial.height/2 - 42  // initial offset from center

                transform: Rotation {
                    angle: -135 + index * 270 / 8
                    origin.x: dial.width/2
                    origin.y: dial.height/2
                }
            }
        }

        // Needle glow
        Rectangle {
            id: needleGlow
            width: 24
            height: dial.height * 0.48
            radius: width / 2
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.verticalCenter
            color: root.redlineColor
            opacity: Math.max(0, (rpmNorm - redlineNorm) * 2)
            transform: Rotation {
                origin.x: width / 2
                origin.y: height
                angle: -135 + rpmNorm * 270
            }
            Behavior on opacity { NumberAnimation { duration: 150 } }
        }

        // Needle
        Rectangle {
            id: needle
            width: 4
            height: dial.height * 0.45
            radius: 2
            color: "red"

            x: dial.width/2 - width/2
            y: dial.height/2 - height  // position bottom of needle at dial center

            transform: Rotation {
                origin.x: width/2
                origin.y: height  // pivot at bottom
                angle: -135 + rpmNorm * 270
                Behavior on angle {
                    NumberAnimation { duration: 120; easing.type: Easing.OutCubic }
                }
            }
        }


        // Center cap
        Rectangle {
            width: 16
            height: 16
            radius: 8
            color: textColor
            anchors.centerIn: parent
        }
    }

    // ====== SHIFT LIGHT ======
    Rectangle {
        id: shiftLight
        width: 80
        height: 20
        radius: 10
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 40
        color: redlineColor
        opacity: 0
        SequentialAnimation on opacity {
            running: rpm >= redlineRpm
            loops: Animation.Infinite
            NumberAnimation { to: 1.0; duration: 120 }
            NumberAnimation { to: 0.2; duration: 120 }
        }
    }

    // ====== DIGITAL RPM ======
    Text {
        text: Math.round(rpm) + " RPM"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 40
        font.pointSize: 24
        font.bold: true
        color: rpm >= redlineRpm ? redlineColor : textColor
    }
}
