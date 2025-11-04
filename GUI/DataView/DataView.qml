import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: dataView
    width: parent ? parent.width : 800
    height: parent ? parent.height : 800

    // --- Data properties ---
    property real velocity: 65.0
    property real tempInside: 22.5
    property real tempOutside: 16.2
    property real humidityInside: 50
    property real humidityOutside: 55
    property real piTemperature: 48.3
    property color textColor: "white"

    // Black background
    Rectangle {
        anchors.fill: parent
        color: "black"
        z: -1   // make sure it stays behind other items
    }

    Column {
        anchors.centerIn: parent
        spacing: 0
        anchors.horizontalCenter: parent.horizontalCenter

        // // --- Velocity ---
        // Rectangle {
        //     id: velocityBox
        //     radius: 12
        //     color: "black"           // dark modern background
        //     border.color: "#00AEEF" // accent border
        //     border.width: 2
        //     anchors.horizontalCenter: parent.horizontalCenter

        //     // size according to content
        //     width: velocityText.implicitWidth + 100   // add some padding
        //     height: velocityText.implicitHeight + 20

        //     Text {
        //         id: velocityText
        //         text: velocity.toFixed(1) + " km/h"
        //         font.pixelSize: 28
        //         font.bold: true
        //         color: textColor
        //         anchors.centerIn: parent
        //     }
        // }

        // --- Gauges ---
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 0   // space between top row and Pi gauge

            // Top row: inside and outside sensors
            Row {
                spacing: 0
                anchors.horizontalCenter: parent.horizontalCenter

                // Inside sensor + icon
                Column {
                    spacing: -20

                    TemperatureAndHumidityGauge {
                        width: 300
                        height: 300
                        temperature: tempInside
                        minTemperature: -20
                        maxTemperature: 50
                        humidity: humidityInside
                        minHumidity: 0
                        maxHumidity: 100
                        showHumidity: true
                        dialColor: textColor
                        needleColor: "#00AEEF"
                    }

                    Image {
                        width: 32
                        height: 32
                        source: "../lib/icons/carIcon.png"
                        fillMode: Image.PreserveAspectFit
                    }
                }

                // Outside sensor + icon
                Column {
                    spacing: -30

                    TemperatureAndHumidityGauge {
                        width: 300
                        height: 300
                        temperature: tempOutside
                        minTemperature: -20
                        maxTemperature: 50
                        humidity: humidityOutside
                        minHumidity: 0
                        maxHumidity: 100
                        showHumidity: true
                        dialColor: textColor
                        needleColor: "#00AEEF"
                    }

                    Image {
                        width: 32
                        height: 32
                        source: "../lib/icons/windIcon.png"
                        fillMode: Image.PreserveAspectFit
                        anchors.horizontalCenter: parent.horizontalCente
                    }
                }
            }

            // Bottom: Raspberry Pi temperature + icon, centered
            Column {
                spacing: 0
                anchors.horizontalCenter: parent.horizontalCenter

                TemperatureAndHumidityGauge {
                    width: 200
                    height: 200
                    temperature: piTemperature
                    minTemperature: 20
                    maxTemperature: 80
                    showHumidity: false
                    dialColor: textColor
                    needleColor: "#FFAA00"
                }

                Image {
                    width: 30
                    height: 30
                    source: "../lib/icons/raspberryPIIcon.png"
                    fillMode: Image.PreserveAspectFit

                }
            }
        }
    }
}
