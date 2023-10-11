from datetime import datetime
from . import db

class Pico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(16), unique=True, nullable=False)

    temperatures = db.relationship('Temperature', backref='pico', lazy=True)
    humidities = db.relationship('Humidity', backref='pico', lazy=True)
    voltages = db.relationship('Voltage', backref='pico', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'unique_id': self.unique_id,
            'temperatures': [temperature.to_dict() for temperature in self.temperatures],
            'humidities': [humidity.to_dict() for humidity in self.humidities],
            'voltages': [voltage.to_dict() for voltage in self.voltages]
        }
    
class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pico_id = db.Column(db.Integer, db.ForeignKey('pico.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat()
        }

class Humidity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pico_id = db.Column(db.Integer, db.ForeignKey('pico.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat()
        }
    
class Voltage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pico_id = db.Column(db.Integer, db.ForeignKey('pico.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat()
        }