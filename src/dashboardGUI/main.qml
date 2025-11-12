import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "GPSView"
import "ClockView"
import "DataView"
import "AccelerationView"

Window {
    id: root
    width: 800
    height: 800
    visible: true
    title: qsTr("Dashboard")

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

    Rectangle {
        id: shutdownBackground
        color: "black"          // Background color
        radius: 10              // Optional: rounded corners
        width: parent.width * 0.6
        height: 80
        anchors.centerIn: parent
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenterOffset: parent.height / 3 
        visible: backend.velocity === 0 

        // Add border
        border.color: "silver"
        border.width: 2          // Small border

        Text {
            id: shutdownMessage
            text: "Hold button to shutdown"
            color: "red"
            font.bold: true
            font.pointSize: 24
            anchors.centerIn: parent
        }
    }

    Behavior on dayColor { ColorAnimation { duration: 2000; easing.type: Easing.InOutQuad } }
}