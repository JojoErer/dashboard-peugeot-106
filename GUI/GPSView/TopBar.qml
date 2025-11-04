import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: topBar
    property color textColor: "yellow"
    anchors {
        left: parent.left
        right: parent.right
        top: parent.top
    }
    color: "black"
    height: parent.height / 8

    property real speed: 0.0 // in km/h, can be updated dynamically

    // Update time every second
    Timer {
        id: clockTimer
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            var now = new Date()
            var hours = now.getHours()
            var minutes = now.getMinutes()
            timeText.text = (hours < 10 ? "0" : "") + hours + ":" +
                            (minutes < 10 ? "0" : "") + minutes
        }
    }

    // Left: Velocity
    Text {
        id: velocityText
        text: speed.toFixed(1) + " km/h"
        color: textColor
        font.pixelSize: parent.height * 0.5
        anchors.verticalCenter: parent.verticalCenter
        anchors {
            horizontalCenter: parent.horizontalCenter
            horizontalCenterOffset: -parent.width/7
            verticalCenter: parent.verticalCenter
            verticalCenterOffset: parent.height * 0.15
            leftMargin: 16
        }
    }

    // Right: Time
    Text {
        id: timeText
        text: "00:00"
        color: textColor
        font.pixelSize: topBar.height * 0.5
        anchors {
            horizontalCenter: parent.horizontalCenter
            horizontalCenterOffset: parent.width/6
            verticalCenter: parent.verticalCenter
            verticalCenterOffset: parent.height * 0.15
            leftMargin: 16
        }
    }
}

