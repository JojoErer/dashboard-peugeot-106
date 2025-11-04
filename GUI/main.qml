import QtQuick
import QtQuick.Window 2.12
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "GPSView"
import "ClockView"
import "DataView"

Window {
    id: root
    width: 800
    height: 800
    visible: true
    title: qsTr("Dashboard")

    // --- Track which view is active ---
    property string currentView: "gps"  // "gps", "clock", "data"

    // --- GPS View ---
    CircleWindow {
        id: gpsView
        anchors.fill: parent
        visible: root.currentView === "gps"
        zoom: 14
        centerLat: 52.107
        centerLon: 5.1214
    }

    // --- Data View ---
    DataView {
        id: statusPanel
        anchors.centerIn: parent
        velocity: 65.0
        tempInside: 2.5
        tempOutside: 16.2
        humidityInside: 50
        humidityOutside: 55
        piTemperature: 10.3
        textColor: "yellow"
        visible: root.currentView === "data"
    }

    // --- Top Bar (only in GPS view) ---
    TopBar {
        id: topBar
        speed: 45
        anchors.top: parent.top
        textColor: "yellow"
        visible: root.currentView === "gps" || root.currentView === "data"
    }

    // --- Bottom Bar (only in GPS view) ---
    BottomBar {
        id: bottomBar
        visible: root.currentView === "gps" || root.currentView === "data"
    }

    // --- Clock View ---
    ClockView {
        id: dashboardClock
        anchors.fill: parent
        visible: root.currentView === "clock"
        clockColor: "yellow"
    }

    // --- Toggle Button ---
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
            id: toggleText
            anchors.centerIn: parent
            color: "white"
            text: {
                if (root.currentView === "gps") return "Show Clock"
                else if (root.currentView === "clock") return "Show Data"
                else return "Show GPS"
            }
            font.pixelSize: 16
        }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                if (root.currentView === "gps") root.currentView = "clock"
                else if (root.currentView === "clock") root.currentView = "data"
                else root.currentView = "gps"
            }
        }
    }
}
