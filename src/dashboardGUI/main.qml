import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "GPSView"
import "ClockView"
import "DataView"
import "AccelerationView"
import "TechnometerViewClassic"
import "TechnometerViewModern"

ApplicationWindow {
    id: root
    visible: true
    visibility: debugOn ? Window.Windowed : Window.FullScreen
    width: Screen.width
    height: Screen.height

    // ====== ARBITRARY ROTATION (degrees) ======
    property real uiRotation: 142

    // ====== Global State ======
    property color dayColor: backend.isDaytime ? "white" :  "#ffd577"

    // ====== ROTATED ROOT ======
    Item {
        id: rotatedRoot
        anchors.centerIn: parent
        width: root.width
        height: root.height

        transform: Rotation {
            angle: root.uiRotation
            origin.x: rotatedRoot.width / 2
            origin.y: rotatedRoot.height / 2
        }

        Behavior on rotation {
            NumberAnimation {
                duration: 80
                easing.type: Easing.InOutQuad
            }
        }

        // ====== VIEWS ======

        // --- GPS Map View ---
        CircleWindow {
            id: gpsView
            anchors.fill: parent
            visible: backend.currentView === "gps"
            zoom: 14
            centerLat: backend.centerLat
            centerLon: backend.centerLon
            darkMode:  backend.isDaytime

            Behavior on centerLat { NumberAnimation { duration: 500; easing.type: Easing.InOutQuad } }
            Behavior on centerLon { NumberAnimation { duration: 500; easing.type: Easing.InOutQuad } }
        }

        // --- Technometer View (Classic) ---
        TechnometerViewClassic {
            id: technoClassic
            anchors.fill: parent
            visible: backend.currentView === "techno" && backend.showOverlays

            rpm: backend.rpm
            textColor: root.dayColor
        }

        // --- Technometer View (Modern) ---
        TechnometerViewModern {
            id: technoModern
            anchors.centerIn: parent
            visible: backend.currentView === "techno" && !backend.showOverlays

            rpm: backend.rpm
            textColor: root.dayColor
        }

        // --- Data Panel ---
        DataView {
            id: statusPanel
            anchors.centerIn: parent
            visible: backend.currentView === "data"

            velocity: backend.velocity
            tempInside: backend.tempInside
            tempOutside: backend.tempOutside
            humidityInside: backend.humidityInside
            humidityOutside: backend.humidityOutside
            piTemperature: backend.piTemperature
            textColor: root.dayColor
        }

        // --- Clock View ---
        ClockView {
            id: dashboardClock
            anchors.fill: parent
            visible: backend.currentView === "clock"

            clockColor: root.dayColor
            gpsTime: backend.gpsTime
        }

        // --- Acceleration View ---
        AccelerationView {
            id: accelView
            anchors.fill: parent
            visible: backend.currentView === "accel"

            ax: backend.ax
            ay: backend.ay
            textColor: root.dayColor
        }

        // ====== UI OVERLAYS ======

        TopBar {
            id: topBar
            anchors.top: parent.top
            speed: backend.velocity
            gpsTime: backend.gpsTime
            textColor: root.dayColor
            visible:
                (backend.currentView === "data" || backend.currentView === "accel")
                || ((backend.currentView === "gps" || backend.currentView === "techno") && !backend.showOverlays)
        }

        BottomBar {
            id: bottomBar
            visible:
                (backend.currentView === "data" || backend.currentView === "accel")
                || ((backend.currentView === "gps" || backend.currentView === "techno") && !backend.showOverlays)
        }

        // ====== SYSTEM / ACTION / SHUTDOWN OVERLAY ======
        Rectangle {
            id: systemMessageBox
            color: "black"
            radius: 10
            border.color: "silver"
            border.width: 3

            property int padding: 16

            property bool hasSensorMessage: backend.sensorStatusMessage !== ""
            property bool hasSystemMessage: backend.systemActionState !== "idle"
            property bool hasShutdownMessage: backend.velocity === 0 && backend.currentView === "clock"

            property bool hasAnyMessage: hasSensorMessage || hasSystemMessage || hasShutdownMessage

            width: hasAnyMessage
                ? Math.max(errorText.implicitWidth + padding * 2,
                            statusText.implicitWidth + padding * 2,
                            actionText.implicitWidth + padding * 2)
                : 0
            height: hasAnyMessage
                    ? Math.max(errorText.implicitHeight + padding * 2,
                            statusText.implicitHeight + padding * 2, 
                            actionText.implicitHeight + padding * 2 + statusText.implicitHeight)
                    : 0
            visible: hasAnyMessage


            anchors.centerIn: parent
            anchors.verticalCenterOffset: parent.height / 4

            Column {
                id: messageColumn
                anchors.centerIn: parent
                spacing: 8
                width: systemMessageBox.width - systemMessageBox.padding * 2

                // --- Sensor Status ---
                Text {
                    id: statusText
                    width: parent.width
                    font.pointSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                    color: backend.sensorStatusMessage.startsWith("All") ? "lime" : "red"
                    visible: backend.sensorStatusMessage !== ""
                    text: backend.sensorStatusMessage
                }

                // --- System Action State ---
                Text {
                    id: actionText
                    width: parent.width
                    font.pointSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    color: "yellow"
                    visible: backend.systemActionState !== "idle"
                    text: {
                        switch(backend.systemActionState) {
                            case "calibrating_mpu": return "Calibrating MPU6050...";
                            case "mpu_done": return "MPU6050 calibration complete";
                            case "mpu_failed": return "MPU6050 calibration failed";
                            case "git_checking": return "Checking for software updates...";
                            case "git_updating": return "Updating software...";
                            case "git_done": return "Update complete";
                            case "git_failed": return "Update failed";
                            default: return "";
                        }
                    }
                }

                // --- Shutdown Instruction ---
                Text {
                    id: errorText
                    width: parent.width
                    font.pointSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    color: "red"
                    visible: backend.velocity === 0 && backend.currentView === "clock"
                    text: "Hold top button to shutdown"
                }
            }

            // ===== Timer to hide messages automatically (except shutdown) =====
            Timer {
                id: hideMessageTimer
                interval: 4000
                repeat: false
                running: (backend.sensorStatusMessage !== "" || backend.systemActionState !== "idle")
                onTriggered: {
                    backend.sensorStatusMessage = ""
                    backend.systemActionState = "idle"
                }
            }

            // ===== Run timer whenever a new message appears =====
            Connections {
                target: backend

                function onSensorStatusMessageChanged() {
                    if (backend.sensorStatusMessage !== "")
                        hideMessageTimer.restart()
                }

                function onSystemActionStateChanged() {
                    if (backend.systemActionState !== "idle")
                        hideMessageTimer.restart()
                }
            }
        }

        // ====== LOADING SCREEN ======

        Rectangle {
            id: loadingOverlay
            anchors.fill: parent
            color: "black"
            visible: true
            opacity: 1.0

            Image {
                id: loadingImage
                source: "../dashboardGUI/lib/peugeot106emblem/PeugeotSilverLogo.png"
                anchors.centerIn: parent
                width: 400
                height: 400
                fillMode: Image.PreserveAspectFit
            }

            SequentialAnimation on opacity {
                running: true
                PropertyAnimation { duration: 1000; to: 1.0 }
                PauseAnimation { duration: 1000 }
                PropertyAnimation {
                    duration: 1000
                    to: 0.0
                    easing.type: Easing.InOutQuad
                }
                onStopped: loadingOverlay.visible = false
            }
        }
    }

    Behavior on dayColor {
        ColorAnimation {
            duration: 200
            easing.type: Easing.InOutQuad
        }
    }
}