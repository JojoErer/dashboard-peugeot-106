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
    property color dayColor: isDaytime ? "white" : "yellow"
    property bool isDaytime: true

    // GPS Route simulation
    property var gpsRoute: [
        { lat: 52.1070, lon: 5.1214 },
        { lat: 52.1075, lon: 5.1222 },
        { lat: 52.1080, lon: 5.1231 },
        { lat: 52.1086, lon: 5.1240 },
        { lat: 52.1092, lon: 5.1235 },
        { lat: 52.1097, lon: 5.1223 },
        { lat: 52.1091, lon: 5.1210 },
        { lat: 52.1083, lon: 5.1205 },
        { lat: 52.1075, lon: 5.1208 },
        { lat: 52.1070, lon: 5.1214 }
    ]
    property int gpsIndex: 0

    // ====== VIEWS ======

    // --- GPS Map View ---
    CircleWindow {
        id: gpsView
        anchors.fill: parent
        visible: root.currentView === "gps"
        zoom: 14
        centerLat: gpsRoute[gpsIndex].lat
        centerLon: gpsRoute[gpsIndex].lon

        Behavior on centerLat { NumberAnimation { duration: 2000; easing.type: Easing.InOutQuad } }
        Behavior on centerLon { NumberAnimation { duration: 2000; easing.type: Easing.InOutQuad } }
    }

    // --- Data Panel ---
    DataView {
        id: statusPanel
        anchors.centerIn: parent
        visible: root.currentView === "data"
        textColor: root.dayColor

        Behavior on textColor { ColorAnimation { duration: 1500 } }
    }

    // --- Clock View ---
    ClockView {
        id: dashboardClock
        anchors.fill: parent
        visible: root.currentView === "clock"
        clockColor: root.dayColor
        gpsTime: simulatedTime
        Behavior on clockColor { ColorAnimation { duration: 1500 } }
    }

    // --- Acceleration View ---
    AccelerationView {
        id: accelView
        anchors.fill: parent
        visible: root.currentView === "accel"
        textColor: root.dayColor

        Behavior on ax { NumberAnimation { duration: 1000; easing.type: Easing.InOutQuad } }
        Behavior on ay { NumberAnimation { duration: 1000; easing.type: Easing.InOutQuad } }
    }

    // ====== UI OVERLAYS ======

    // --- Top Bar (updated for GPS time input) ---
    TopBar {
        id: topBar
        anchors.top: parent.top
        speed: statusPanel.velocity
        gpsTime: simulatedTime
        textColor: root.dayColor
        visible: root.currentView !== "clock"

        Behavior on speed { NumberAnimation { duration: 1000; easing.type: Easing.InOutQuad } }
        Behavior on textColor { ColorAnimation { duration: 1500 } }
    }

    // --- Bottom Bar (simplified) ---
    BottomBar {
        id: bottomBar
        visible: root.currentView !== "clock"
    }

    // --- View Toggle Button ---
    Rectangle {
        id: toggleButton
        width: 180
        height: 40
        radius: 8
        color: "#222"
        border.color: "white"
        border.width: 2
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 10

        Text {
            anchors.centerIn: parent
            color: "white"
            font.pixelSize: 16
            text: {
                switch (root.currentView) {
                    case "gps": return "Show Clock"
                    case "clock": return "Show Data"
                    case "data": return "Show Acceleration"
                    default: return "Show GPS"
                }
            }
        }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                switch (root.currentView) {
                    case "gps": root.currentView = "clock"; break
                    case "clock": root.currentView = "data"; break
                    case "data": root.currentView = "accel"; break
                    default: root.currentView = "gps"
                }
            }
        }
    }

    // ====== TIMERS & SIMULATION ======

    // Simulated GPS movement
    Timer {
        id: gpsMover
        interval: 2000
        running: true
        repeat: true
        onTriggered: {
            gpsIndex = (gpsIndex + 1) % gpsRoute.length
            gpsView.centerLat = gpsRoute[gpsIndex].lat
            gpsView.centerLon = gpsRoute[gpsIndex].lon
        }
    }

    // Simulated sensor + system data
    Timer {
        id: sensorSimulator
        interval: 1000
        running: true
        repeat: true
        onTriggered: simulateSensorData()
    }

    // Simulated GPS Time
    property string simulatedTime: "00:00"
    Timer {
        id: timeSim
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            var now = new Date()
            var h = now.getHours()
            var m = now.getMinutes()
            simulatedTime = (h < 10 ? "0" : "") + h + ":" + (m < 10 ? "0" : "") + m
        }
    }

    // Day/Night color toggle
    Timer {
        id: dayNightTimer
        interval: 10000
        running: true
        repeat: true
        onTriggered: root.isDaytime = !root.isDaytime
    }

    Behavior on dayColor { ColorAnimation { duration: 2000; easing.type: Easing.InOutQuad } }

    // ====== FUNCTIONS ======
    function simulateSensorData() {
        function rand(min, max) { return Math.random() * (max - min) + min }

        statusPanel.velocity = rand(40, 120)
        statusPanel.tempInside = rand(18, 28)
        statusPanel.tempOutside = rand(5, 35)
        statusPanel.humidityInside = rand(40, 60)
        statusPanel.humidityOutside = rand(45, 70)
        statusPanel.piTemperature = rand(30, 60)
        accelView.ax = rand(-4, 4)
        accelView.ay = rand(-4, 4)
    }
}
