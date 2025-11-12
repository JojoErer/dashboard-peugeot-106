import QtQuick 2.15

Rectangle {
    id: bottomBar
    property alias logoSource: carEmblem.source
    property color barColor: "black"
    property real logoScale: 0.8

    anchors {
        left: parent.left
        right: parent.right
        bottom: parent.bottom
    }

    height: parent.height / 8
    color: barColor

    Image {
        id: carEmblem
        anchors.centerIn: parent
        source: "../lib/peugeotLogo/peugeotLogoSilver.png"
        height: parent.height * logoScale
        fillMode: Image.PreserveAspectFit
    }
}
