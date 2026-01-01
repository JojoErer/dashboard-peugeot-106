import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    width: parent ? parent.width : 800
    height: parent ? parent.height : 400

    // ===== DATA =====
    property real rpm: 0
    property real maxRpm: 7000
    property real redlineRpm: 6000

    readonly property real rpmNorm: Math.min(rpm / maxRpm, 1)
    readonly property bool inRedZone: rpmNorm >= 0.8

    // ===== COLORS =====
    property color bgColor: "black"
    property color inactiveColor: "#222"
    property color greenColor: "#00ff66"
    property color blueColor: "#00c8ff"
    property color redColor: "#ff3b3b"
    property color textColor: "white"

    // Shift light thresholds
    property var shiftLights: [
        0.2, 0.3, 0.4,
        0.5, 0.6,
        0.7, 0.8, 0.9
    ]

    // ===== GLOBAL 1 Hz BLINKER =====
    property real blinkPhase: 1.0

    SequentialAnimation on blinkPhase {
        running: inRedZone
        loops: Animation.Infinite
        NumberAnimation { to: 0.2; duration: 500 }  // off
        NumberAnimation { to: 1.0; duration: 500 }  // on
    }

    Rectangle {
        anchors.fill: parent
        color: bgColor
    }

    Item {
        id: gauge
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.8
        height: parent.height * 0.5

        // ===== SHIFT LIGHTS =====
        Row {
            id: lightsRow
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: bar.top
            anchors.bottomMargin: lightSize * 0.8
            spacing: lightSize * 0.4

            property real lightSize: bar.height * 0.6

            Repeater {
                model: shiftLights.length

                Item {
                    width: lightsRow.lightSize
                    height: width

                    readonly property bool active: rpmNorm >= shiftLights[index]
                    readonly property color ledColor: {
                        if (!active) return inactiveColor
                        if (index < 3) return greenColor
                        if (index < 5) return blueColor
                        return redColor
                    }

                    // Fake glow
                    Rectangle {
                        anchors.centerIn: parent
                        width: parent.width * 1.6
                        height: width
                        radius: width / 2.5
                        color: ledColor
                        opacity: active ? (inRedZone ? blinkPhase * 0.25 : 0.25) : 0
                        visible: active
                    }

                    // LED core
                    Rectangle {
                        anchors.fill: parent
                        radius: width / 2
                        color: ledColor
                        opacity: active ? (inRedZone ? blinkPhase : 1.0) : 0.4
                    }
                }
            }
        }

        // ===== BAR BACKGROUND =====
        Rectangle {
            id: bar
            anchors.verticalCenter: parent.verticalCenter
            width: parent.width
            height: parent.height * 0.12
            radius: height / 2
            color: inactiveColor
            clip: true

            // ===== CLIP CONTAINER =====
            Item {
                width: bar.width * rpmNorm
                height: parent.height
                clip: true

                Behavior on width {
                    NumberAnimation {
                        duration: 80
                        easing.type: Easing.OutCubic
                    }
                }

                // ===== FULL GRADIENT (FIXED WIDTH) =====
                Rectangle {
                    width: bar.width         
                    height: parent.height
                    radius: height / 2

                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0; color: greenColor }
                        GradientStop { position: 0.2; color: greenColor }
                        GradientStop { position: 0.2; color: blueColor }
                        GradientStop { position: 0.5; color: blueColor }
                        GradientStop { position: 0.5; color: redColor }
                        GradientStop { position: 1.0; color: redColor }
                    }
                }
            }
        }

        // ===== RPM TEXT =====
        Text {
            anchors.top: bar.bottom
            anchors.topMargin: bar.height * 0.8
            anchors.horizontalCenter: parent.horizontalCenter

            text: Math.round(rpm) + " tr/min"
            color: textColor
            font.pixelSize: bar.height * 0.75
            font.bold: true
        }
    }
}
