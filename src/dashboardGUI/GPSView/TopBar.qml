import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: topBar
    anchors {
        left: parent.left
        right: parent.right
        top: parent.top
    }

    height: parent.height / 8
    color: "black"

    // === Public properties ===
    property color textColor: "yellow"
    property real speed: 0.0        // km/h, can be updated externally
    property string gpsTime: "00:00" // time string (HH:MM) from GPS

    // === Speed Display ===
    Text {
        id: velocityText
        anchors {
            verticalCenter: parent.verticalCenter
            horizontalCenter: parent.horizontalCenter
            horizontalCenterOffset: -parent.width * 0.15
        }
        color: topBar.textColor
        textFormat: Text.RichText
        text: `
            <span style="font-size:${parent.height * 0.5}px;">
                ${speed.toFixed(1)}
            </span>
            <span style="font-size:${parent.height * 0.25}px;">
                km/h
            </span>
        `
    }

    // === Time Display (from GPS) ===
    Text {
        id: timeText
        anchors {
            verticalCenter: parent.verticalCenter
            horizontalCenter: parent.horizontalCenter
            horizontalCenterOffset: parent.width * 0.15
        }
        color: topBar.textColor
        font.pixelSize: parent.height * 0.5
        text: gpsTime
    }
}
