# mokki-flask

Project files for Flask server communicating with Raspberry Pi Pico via Bluetooth and MQTT. Raspberry Pi Pico project files are [here](https://github.com/teemueer/mokki-pico)

## Installation

### MQTT

`sudo apt-get install mosquitto mosquitto-clients`

Server is configured to use OpenSSL certificates by default.

### InfluxDB

Install InfluxDB 2.0 with instructions on their [site](https://docs.influxdata.com/influxdb/v2/install/).

### Generating TPM secrets

Script for generating secrets for devices [here](https://github.com/teemueer/mokki-flask/blob/master/management/tpm.sh)

### Packages

Install required packages with

`pip install -r requirements.txt`

### Environment values

| Environment value | Description |
| --- | --- |
| JWT_SECRET_KEY | Secret key for JWT |
| WLAN_SSID | Wireless SSID which is sent to Pico |
| WLAN_PASSWORD | Wireless password which is sent to Pico |
| INFLUXDB_URL | InfluxDB URL |
| INFLUXDB_TOKEN | InfluxDB token |
| INFLUXDB_ORG | InfluxDB organization |
| MQTT_BROKER_URL | MQTT broker URL |
| MQTT_TLS_CA_CERTS | OpenSSL certificate path |

### Initializng the database

`flask db init`

`flask db migrate`

`flask db upgrade`

### Starting server

`python run.py`

## Sequence diagrams

### Setup

![Setup](https://github.com/teemueer/mokki-flask/blob/master/diagrams/init.drawio.png)


### Bluetooth mode

![Pairing](https://github.com/teemueer/mokki-flask/blob/master/diagrams/pairing.drawio.png)


### Sensor mode

![Setup](https://github.com/teemueer/mokki-flask/blob/master/diagrams/sensor.drawio.png)
