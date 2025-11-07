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

    // ====== Data from Python ======
    //property string gpsTime: "00:00"       // Updated by Python
    //property double velocity: 0            // Updated by Python
    //property double tempInside: 0          // Updated by Python
    //property double tempOutside: 0         // Updated by Python
    //property double humidityInside: 0      // Updated by Python
    //property double humidityOutside: 0     // Updated by Python
    //property double piTemperature: 0       // Updated by Python
    //property double ax: 0                  // Updated by Python
    //property double ay: 0                  // Updated by Python
    //property double centerLat: 52.1070     // GPS Latitude from Python
    //property double centerLon: 5.1214      // GPS Longitude from Python

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
    }

    // ====== UI OVERLAYS ======
    TopBar {
        id: topBar
        anchors.top: parent.top
        speed: backend.velocity
        gpsTime: backend.gpsTime
        textColor: root.dayColor
        visible: root.currentView !== "clock"
    }

    BottomBar {
        id: bottomBar
        visible: root.currentView !== "clock"
    }

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
}
