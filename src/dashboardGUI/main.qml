import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "GPSView"
import "ClockView"
import "DataView"
import "AccelerationView"

ApplicationWindow {
    id: root
    visible: true
    visibility: Window.FullScreen
    width: Screen.width
    height: Screen.height

    // ====== Global State ======
    property bool isDaytime: backend.isDaytime
    property color dayColor: backend.isDaytime ? "white" : "#FFDF00"
    property bool showOverlays: backend.showOverlays


    // ====== VIEWS ======

    // --- GPS Map View ---
    CircleWindow {
        id: gpsView
        anchors.fill: parent
        visible: backend.currentView === "gps"
        zoom: 14
        centerLat: backend.centerLat
        centerLon: backend.centerLon

        Behavior on centerLat { NumberAnimation { duration: 500; easing.type: Easing.InOutQuad } }
        Behavior on centerLon { NumberAnimation { duration: 500; easing.type: Easing.InOutQuad } }
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
        calibrationState: backend.calibrationState
    }

    // ====== UI OVERLAYS ======
    TopBar {
        id: topBar
        anchors.top: parent.top
        speed: backend.velocity
        gpsTime: backend.gpsTime
        textColor: root.dayColor
        // Visible only if not in clock view, and in GPS view only if overlays are enabled
        visible: backend.currentView !== "clock" && (backend.currentView !== "gps" || root.showOverlays)
    }

    BottomBar {
        id: bottomBar
        visible: backend.currentView !== "clock" && (backend.currentView !== "gps" || root.showOverlays)
    }

    // ====== SYSTEM STATUS / SHUTDOWN MESSAGE ======
    Rectangle {
        id: shutdownBackground
        color: "black"
        radius: 10
        border.color: "silver"
        border.width: 2

        // Padding around the text
        property int padding: 16

        // Dynamic sizing based on text content
        width: Math.min(parent.width * 0.9, statusText.paintedWidth + padding * 2)
        height: statusText.paintedHeight + padding * 2

        anchors.centerIn: parent
        anchors.verticalCenterOffset: parent.height / 4

        visible: backend.velocity === 0

        Text {
            id: statusText
            anchors.centerIn: parent
            color: backend.sensorStatusMessage.startsWith("All") ? "lime" : "red"
            font.bold: true
            font.pointSize: 16
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.WordWrap
            width: shutdownBackground.width - shutdownBackground.padding * 2
            text: backend.sensorStatusMessage
        }

        Timer {
            id: startupTimer
            interval: 10000   // 10 seconds
            running: true
            repeat: false
            onTriggered: {
                statusText.text = "Hold button in clock view to shutdown"
                statusText.color = "red"
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

        // Fade-out animation after 2 seconds
        SequentialAnimation on opacity {
            running: true
            PropertyAnimation { duration: 2000; to: 1.0 } // show for 2 seconds
            PauseAnimation { duration: 2000 } // stay visible for 2 seconds
            PropertyAnimation { duration: 1000; to: 0.0; easing.type: Easing.InOutQuad } // fade out
            onStopped: loadingOverlay.visible = false
        }
    }

    Behavior on dayColor { ColorAnimation { duration: 2000; easing.type: Easing.InOutQuad } }
}