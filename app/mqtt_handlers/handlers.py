import json
from flask import current_app
from paho.mqtt.client import MQTT_LOG_ERR, MQTT_LOG_WARNING
from app.models import Pico, Temperature, Humidity, Voltage

def setup_handlers(app, mqtt, db):

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        mqtt.subscribe('mokki/#')

    @mqtt.on_message()
    def handle_message(client, userdata, message):
        data = json.loads(message.payload.decode())

        pico_id = data['id']
        temperature = data['dht22']['temperature']
        humidity = data['dht22']['humidity']
        voltage = data['ky018']['voltage']

        print(pico_id, temperature, humidity, voltage)

        with app.app_context():
            pico = Pico.query.filter_by(unique_id=pico_id).first()
            if not pico:
                pico = Pico(unique_id=pico_id)
                db.session.add(pico)
                db.session.commit()

            new_temperature = Temperature(value=temperature, pico_id=pico.id)
            new_humidity = Humidity(value=humidity, pico_id=pico.id)
            new_voltage = Voltage(value=voltage, pico_id=pico.id)

            db.session.add(new_temperature)
            db.session.add(new_humidity)
            db.session.add(new_voltage)
            db.session.commit()

        

    @mqtt.on_log()
    def handle_logging(client, userdata, level, buf):
        if level == MQTT_LOG_ERR:
            print(f'WARNING: {buf}')
        elif level == MQTT_LOG_ERR:
            print(f'ERROR: {buf}')
