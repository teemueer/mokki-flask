import json
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from app import mqtt, influx_db
from app.models.device import DeviceModel


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("data/#")


@mqtt.on_message()
def handle_message(client, userdata, message):
    try:
        uid = message.topic.split("/")[1]
        payload = message.payload.decode()
        data = json.loads(payload)
    except:
        return

    with mqtt.app.app_context():
        device = DeviceModel.find_by_uid(uid)
        if not device:
            print("No such device")
            return

        point = (
            Point("sensor_data")
            .tag("device", device.uid)
            .field("temperature", data["temperature"])
            .field("humidity", data["humidity"])
            .field("light_level", data["light_level"])
        )

        # print(point)

        write_api = influx_db.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket="mokki", org="sensec", record=point)
