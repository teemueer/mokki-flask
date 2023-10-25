from app import mqtt


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("mokki/#")


@mqtt.on_message()
def handle_message(client, userdata, message):
    data = message.payload.decode()
    print(data)
