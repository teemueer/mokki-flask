# mokki-flask

Project files for Flask server communicating with Raspberry Pi Pico via Bluetooth and MQTT. Raspberry Pi Pico project files are [here](https://github.com/teemueer/mokki-pico)

## Installation

### MQTT

`sudo apt-get install mosquitto mosquitto-clients`

Server is configured to use OpenSSL certificates by default.

### InfluxDB

Install InfluxDB 2.0 with instructions on their [site](https://docs.influxdata.com/influxdb/v2/install/).

### Packages

Install required packages with

`pip install -r requirements.txt`

### Initializng the database

`flask db init`

`flask db migrate`

`flask db upgrade`

### Generating TPM secrets

Script for generating secrets for devices [here](https://github.com/teemueer/mokki-flask/blob/master/management/tpm.sh)

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

### Starting server

`python run.py`

The user that executes the script needs to belong to bluetooth and tss groups.

## Sequence diagrams

### Setup

![Setup](https://github.com/teemueer/mokki-flask/blob/master/diagrams/init.drawio.png)


### Bluetooth mode

![Pairing](https://github.com/teemueer/mokki-flask/blob/master/diagrams/pairing.drawio.png)


### Sensor mode

![Setup](https://github.com/teemueer/mokki-flask/blob/master/diagrams/sensor.drawio.png)
