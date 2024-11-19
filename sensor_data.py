import RPi.GPIO as GPIO
from flask import Flask, jsonify

# Initialize GPIO
GPIO.setmode(GPIO.BCM)

# Assign GPIO pins to sensors
sensors = {
    "sensor1": 17,
    "sensor2": 18,
    "sensor3": 27,
    "sensor4": 22,
    "sensor5": 23,
}

# Initialize counters
counters = {sensor: 0 for sensor in sensors}

# Set up GPIO inputs
for sensor, pin in sensors.items():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Flask app
app = Flask(__name__)

# Route to fetch counter values
@app.route('/get_counters', methods=['GET'])
def get_counters():
    return jsonify(counters)

# Background function to increment counters based on sensor signal
def update_counters(channel):
    for sensor, pin in sensors.items():
        if pin == channel:
            counters[sensor] += 1

# Register event detection
for pin in sensors.values():
    GPIO.add_event_detect(pin, GPIO.RISING, callback=update_counters)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
