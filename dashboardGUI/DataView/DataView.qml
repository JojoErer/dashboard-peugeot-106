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

        // --- Gauges ---
        Column {
            spacing: -38  // space between top row and Pi gauge

            // Top row: inside and outside sensors
            Row {
                spacing: -10


                // Inside sensor + icon
                Column {
                    spacing: -10

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
                        needleColor: textColor // "#FFAA00"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Image {
                        width: 32
                        height: 32
                        source: "../lib/icons/carIcon.png"
                        anchors.horizontalCenter: parent.horizontalCenter
                        fillMode: Image.PreserveAspectFit
                    }
                }

                // Outside sensor + icon
                Column {
                    spacing: -10

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
                        needleColor: textColor //"#FFAA00"
                    }

                    Image {
                        width: 32
                        height: 32
                        source: "../lib/icons/windIcon.png"
                        anchors.horizontalCenter: parent.horizontalCenter
                        fillMode: Image.PreserveAspectFit
                    }
                }
            }

            // Bottom: Raspberry Pi temperature + icon, centered
            Column {
                spacing: 0
                anchors.horizontalCenter: parent.horizontalCenter

                TemperatureAndHumidityGauge {
                    width: 240
                    height: 240
                    temperature: piTemperature
                    minTemperature: 20
                    maxTemperature: 80
                    showHumidity: false
                    dialColor: textColor
                    needleColor: textColor // "#FFAA00"
                }

                Image {
                    width: 30
                    height: 30
                    source: "../lib/icons/raspberryPIIcon.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    fillMode: Image.PreserveAspectFit

                }
            }
        }
    }
}
