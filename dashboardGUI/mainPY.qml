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
    property string currentView: "gps"    // "gps", "clock", "data", "accel"
    property bool isDaytime: backend.isDaytime
    property color dayColor: backend.isDaytime ? "white" : "yellow"
    property bool showOverlays: true

    // ====== VIEWS ======

    // --- GPS Map View ---
    CircleWindow {
        id: gpsView
        anchors.fill: parent
        visible: root.currentView === "gps"
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
        visible: root.currentView === "data"

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
        visible: root.currentView === "clock"

        clockColor: root.dayColor
        gpsTime: backend.gpsTime
    }

    // --- Acceleration View ---
    AccelerationView {
        id: accelView
        anchors.fill: parent
        visible: root.currentView === "accel"

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
        visible: root.currentView !== "clock" && (root.currentView !== "gps" || root.showOverlays)
    }

    BottomBar {
        id: bottomBar
        visible: root.currentView !== "clock" && (root.currentView !== "gps" || root.showOverlays)
    }

    Behavior on dayColor { ColorAnimation { duration: 2000; easing.type: Easing.InOutQuad } }

    Connections {
        target: backend
        function onNextViewRequested() {
        switch (root.currentView) {
            case "gps": root.currentView = "clock"; break
            case "clock": root.currentView = "data"; break
            case "data": root.currentView = "accel"; break
            default: root.currentView = "gps"
            }
        console.log("View switched to:", root.currentView)
        }

        function onNextOverlayRequested() {
            if (root.currentView === "gps") {
                root.showOverlays = !root.showOverlays
                console.log("Overlays toggled:", root.showOverlays)
            }

            if (root.currentView === "accel") {
                root.showOverlays = !root.showOverlays
                console.log("Calibrating MPU6050:", root.showOverlays)
            }
        }
    }
}
