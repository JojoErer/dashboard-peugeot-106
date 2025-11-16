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

    property color textColor: "white"
    property real speed: 0.0
    property string gpsTime: "00:00"

    Column {
        id: displayColumn
        anchors.centerIn: parent
        spacing: topBar.height * 0.05

        // Time
        Text {
            id: timeText
            color: topBar.textColor
            font.pixelSize: topBar.height * 0.35
            horizontalAlignment: Text.AlignHCenter
            width: topBar.width   // or just remove this line
            text: gpsTime
        }

        // Speed
        Text {
            id: velocityText
            color: topBar.textColor
            textFormat: Text.RichText
            horizontalAlignment: Text.AlignHCenter
            width: topBar.width   // or remove
            text: `
                <span style="font-size:${topBar.height * 0.4}px;">
                    ${speed.toFixed(1)}
                </span>
                <span style="font-size:${topBar.height * 0.2}px;">
                    km/h
                </span>
            `
        }
    }
}
