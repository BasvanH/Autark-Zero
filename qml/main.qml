import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14
import QtPositioning 5.15
import QtLocation 5.15


ApplicationWindow {
    width: 1280
    height: 720
    visible: true
    title: qsTr("Geo Debug")
    id: window

    property int amplitude: 50
    property int simspeed: 2

    menuBar: MenuBar {
        Menu {
            title: qsTr("&Controls")
            MenuItem {
                text: qsTr("&Load Current Geofence")
                onTriggered: ardupilotFenceGenerator.fetchPolygon()
            }
            MenuItem {
                text: qsTr("&Mission Thing")
                onTriggered: missionList.addSignal()
            }
            MenuItem {
                text: qsTr("&Exit")
                onTriggered: Qt.quit();
            }
        }
    }

    // For the stack layout view
    StackLayout {
        width: parent.width
        currentIndex: tabbar.currentIndex
        Item {
            id: homeTab
        }
        Item {
            id: discoverTab
        }
        Item {
            id: activityTab
        }
    }

    //connecting stack layout to the drawer
    Drawer {
        id: drawer
        property int drawerSize: 2
        width: 400
        height: window.height
        //Tab bar that connects to the stack layout
        TabBar {
            id: tabbar
            width: drawer.width
            //different values
            TabButton {
                text: qsTr("Simulation Settings")
            }
            TabButton {
                text: qsTr("Value Settings")
            }
            TabButton {
                text: qsTr("Compass Data")
            }
        }
        //defining individual components in detail and customising them
        StackLayout {
            currentIndex: tabbar.currentIndex
            //custom view for the simulation settings
            Item {
                id: simulationsettings
                ColumnLayout {
                    id: simulationlayout
                    spacing: 6
                    anchors.leftMargin: 5
                    anchors.topMargin: 10

                    RowLayout {
                        spacing: 2
                        Layout.topMargin: 80
                        Layout.leftMargin: 100
                        Dial {
                            id: speedslider
                            implicitWidth: 150
                            implicitHeight: 150
                            from: 0
                            to: 200
                            value: amplitude
                        }
                    }

                    Label {
                        text: "Course Amplitude"
                        Layout.bottomMargin: 20
                        font.pixelSize: 20
                        Layout.leftMargin: 100
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        Dial {
                            id: simspeedslider
                            implicitWidth: 150
                            implicitHeight: 150
                            from: 0
                            to: 10
                            value: simspeed
                        }
                    }

                    Label {
                        text: "Simulation Speed"
                        Layout.bottomMargin: 28
                        font.pixelSize: 20
                        Layout.leftMargin: 100
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 95
                        Button {
                            implicitWidth: 160
                            implicitHeight: 50
                            text: "Load GeoFence"
                            id: loadgeofencebutton
                            onClicked: polygonGenerator.drawWaterOutline()
                        }
                    }
                }
            }

            Item {
                id: valuesettings
                ColumnLayout {
                    id: valuelayout
                    spacing: 6
                    anchors.leftMargin: 5
                    anchors.topMargin: 10

                    Label {
                        text: "Geofence"
                        Layout.topMargin: 80
                        Layout.leftMargin: 140
                        font.pixelSize: 20
                    }

                    RowLayout{
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField {
                            id: latitudevaluedelta
                            text: config.general_getter('GEOFENCE', 'LATITUDE_DELTA')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }

                        }
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField {
                            id: longitudevaluedelta
                            text: config.general_getter('GEOFENCE', 'LONGITUDE_DELTA')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }
                        }
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField {
                            id: minrefreshdist
                            text: config.general_getter('GEOFENCE', 'MINIMUM_REFRESH_DISTANCE')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }
                        }
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField {
                            id: refreshdelay
                            text: config.general_getter('GEOFENCE', 'REFRESH_DELAY')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }
                        }
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField{
                            id: simptoledistance
                            text: config.general_getter('GEOFENCE', 'SIMPLIFICATION_TOLERANCE_DISTANCE')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }
                        }
                    }

                    Label {
                        text: "MQTT Config"
                        Layout.topMargin: 20
                        Layout.leftMargin: 140
                        font.pixelSize: 20
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField {
                            id: brokername
                            text: config.general_getter('MQTT_CONFIG', 'BROKER')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }
                        }
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField {
                            id: clientname
                            text: config.general_getter('MQTT_CONFIG', 'CLIENT_NAME')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }
                        }
                    }

                    Label {
                        text: "Mission Planner"
                        font.pixelSize: 20
                        Layout.topMargin: 20
                        Layout.leftMargin: 140
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField {
                            id: arduwaypointlimit
                            text: config.general_getter('MISSION_PLANNER', 'LIMIT_ARDUPILOT_WAYPOINTS')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }
                        }
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField {
                            id: mindistancewaypoints
                            text: config.general_getter('MISSION_PLANNER', 'MINIMUM_DISTANCE_WAYPOINT')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }
                        }
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 100
                        TextField {
                            id: directionangle
                            text: config.general_getter('PATH_FINDER', 'DIRECTION_CHANGE_ANGLE')
                            background: Rectangle {
                                implicitWidth: 220
                                implicitHeight: 40
                                border.color: "#21be2b"
                            }
                        }
                    }

                    RowLayout {
                        spacing: 2
                        Layout.leftMargin: 130
                        Layout.topMargin: 10
                        Button {
                            id: applysettings
                            implicitWidth: 160
                            implicitHeight: 50
                            text: "Apply Settings"
                            onClicked: {
                                config.write_to_file('GEOFENCE', 'LATITUDE_DELTA', latitudevaluedelta.text)
                                config.write_to_file('GEOFENCE', 'LONGITUDE_DELTA', longitudevaluedelta.text)
                                config.write_to_file('GEOFENCE', 'MINIMUM_REFRESH_DISTANCE', minrefreshdist.text)
                                config.write_to_file('GEOFENCE', 'REFRESH_DELAY', refreshdelay.text)
                                config.write_to_file('GEOFENCE', 'SIMPLIFICATION_TOLERANCE_DISTANCE', simptoledistance.text)
                                config.write_to_file('MQTT_CONFIG', 'BROKER', brokername.text)
                                config.write_to_file('MQTT_CONFIG', 'CLIENT_NAME', clientname.text)
                                config.write_to_file('MISSION_PLANNER', 'LIMIT_ARDUPILOT_WAYPOINTS', arduwaypointlimit.text)
                                config.write_to_file('MISSION_PLANNER', 'MINIMUM_DISTANCE_WAYPOINT', mindistancewaypoints.text)
                                config.write_to_file('PATH_FINDER', 'DIRECTION_CHANGE_ANGLE', directionangle.text)
                            }
                        }
                    }
                }
            }
        }
    }

    Map {
        id: map
        visible: true
        property double lat: 52.40359289862932
        property double lon: 4.662117677145794
        anchors.fill: parent
        zoomLevel: 14
        center {
            latitude: lat
            longitude: lon
        }

        plugin: Plugin {
            locales: "en-UK"
            name: "osm"

            // These are required for Windows plebians because TLS is a fickle mistress
            PluginParameter {
                name: "osm.mapping.providersrepository.disabled"
                value: "true"
            }

            PluginParameter {
                name: "osm.mapping.providersrepository.address"
                value: "http://maps-redirect.qt.io/osm/5.15.4/"
            }
        }

        MapPolyline {
            id: road
            line.color: 'red'
            line.width: 5
            opacity: 0.8
            path: [
                QtPositioning.coordinate(52.40359289862932, 4.662117677145794),
                QtPositioning.coordinate(52.40359289862932, 4.662117677145794)
            ]
        }

        MapQuickItem {
            id: boat
            coordinate: QtPositioning.coordinate(52.404729914778514, 4.662558537905132)
            anchorPoint.x: image.width / 2
            anchorPoint.y: image.height / 2
            zoomLevel: 14
            sourceItem: Image {
                id: image
                source: "https://www.clipartkey.com/mpngs/b/150-1500997_pier-clipart.png"
                width: 3
                height: 7
                onStatusChanged: {
                    if (status == Image.Ready) {
                        movement.start()
                    }
                }
            }
        }

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            onClicked: {
                if (mouse.button === Qt.RightButton) contextMenu.popup()
            }
        }

        Menu {
            id: contextMenu

            MenuItem {
                text: 'Draw Debug Geofence'
                onTriggered: {
                    let menuPos = Qt.point(contextMenu.x, contextMenu.y)
                    let coords = map.toCoordinate(menuPos, true)
                    debugFenceGenerator.fetchPolygon(coords.latitude, coords.longitude)
                }
            }

            MenuItem {
                text: 'Set Trip Destination'
                onTriggered: {
                    let menuPos = Qt.point(contextMenu.x, contextMenu.y)
                    let coords = map.toCoordinate(menuPos, true)
                    missionList.createPath(
                        boat.coordinate.latitude, boat.coordinate.longitude,
                        coords.latitude, coords.longitude)
                }
            }
        }
    }

    Connections {
        target: missionList
        function onMissionChanged() {
            if (! road.visible) {
                road.visible = true;
                let next = missionList.get(0)
                movement.i = 1;
                road.replaceCoordinate(1, QtPositioning.coordinate(next.latitude, next.longitude))
                movement.start();
            }
        }
    }

    // Start geofence debug polygon management
    property var lastFence: ({})

    function drawPolygon(polygon) {
        var component = Qt.createComponent("mappolygon.qml");
        var coordinates = []

        for (const element of polygon.perimeter) {
            coordinates.push(element);
        }

        map.removeMapItem(lastFence)
        lastFence = component.createObject(map, { "path": coordinates});
        map.addMapItem(lastFence);
    }

    Connections {
        target: ardupilotFenceGenerator
        function onPolygonChanged(x) {drawPolygon(x)}
    }

    Connections {
        target: debugFenceGenerator
        function onPolygonChanged(x) {drawPolygon(x)}
    }
    // End geofence debug polygon management

    Timer {
        id: movement
        property int value: 0
        property alias speed: speedslider.value;
        property int i: 0

        interval: simspeedslider.value
        running: false
        repeat: true
        onTriggered: {
            value++;

            if (value == speed) {
                let next = missionList.get(movement.i++)

                if (!next.isValid) {
                    movement.stop();
                    missionList.clear();
                    road.visible = false;
                    i = 0;
                    value = 0;
                    road.replaceCoordinate(0, road.path[1]);
                    return;
                }

                road.replaceCoordinate(0, road.path[1])
                road.replaceCoordinate(1, QtPositioning.coordinate(next.latitude, next.longitude))
                value = 0;

            }

            let amplitude = QtPositioning.coordinate(
                road.path[1].latitude - road.path[0].latitude,
                road.path[1].longitude - road.path[0].longitude)

            boat.coordinate.latitude =  road.path[0].latitude + amplitude.latitude * value * 1/speed;
            boat.coordinate.longitude = road.path[0].longitude + amplitude.longitude * value * 1/speed;
        }
    }

    PositionSource {
        onPositionChanged:  {
            map.center = position.coordinate
        }
    }
}
