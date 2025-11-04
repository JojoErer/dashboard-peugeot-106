import QtQuick 2.15

Rectangle{
    id: bottomBar
    anchors {
        left: parent.left
        right: parent.right
        bottom: parent.bottom
    }
    color: 'black'
    height: parent.height/8

    Image {
        id: carEmblem
        anchors{
            centerIn: parent
            verticalCenterOffset: -parent.height * 0.15
        }
        source: "../lib/peugeotLogo/peugeot106Silver.png"
        width: parent.width * .3
        height: parent.height* 0.6
    }
}
