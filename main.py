import RPi.GPIO as GPIO
import time
import threading
import csv
from flask import Flask, jsonify, render_template_string
from datetime import datetime

# Set up GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering

# Define the GPIO pins for the buttons
BUTTON_PINS = [16, 19, 26, 20, 21]

# Set up each button pin as input with internal pull-up resistors
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Flask app setup
app = Flask(__name__)

# Button press counts dictionary
press_counts = {pin: 0 for pin in BUTTON_PINS}
button_states = {pin: GPIO.HIGH for pin in BUTTON_PINS}  # Track the current state (released or pressed)
total_count = 0  # Accumulated total count

# Function to save counts to a CSV file
def save_counts_to_file():
    filename = datetime.now().strftime("%Y-%m-%d.csv")  # File name based on the current date
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['GPIO Pin', 'Press Count'])
        for pin, count in press_counts.items():
            writer.writerow([pin, count])
        writer.writerow(['Total', total_count])

# Function to count button presses with edge detection
def count_button_presses():
    global press_counts, button_states, total_count
    while True:
        for pin in BUTTON_PINS:
            input_state = GPIO.input(pin)
            if input_state == GPIO.LOW and button_states[pin] == GPIO.HIGH:  # Button pressed
                press_counts[pin] += 1
                total_count += 1  # Update the total count
                print(f"Button on GPIO {pin} pressed. Total Count: {total_count}")  # Log to console
                save_counts_to_file()  # Save changes to file
                button_states[pin] = GPIO.LOW  # Update state to pressed
                time.sleep(0.2)  # Debounce delay
            elif input_state == GPIO.HIGH and button_states[pin] == GPIO.LOW:  # Button released
                button_states[pin] = GPIO.HIGH  # Update state to released

# Route to serve the main page with the total count
@app.route('/')
def home():
    return render_template_string(html_template, total_count=total_count)

# Route to return the current total count dynamically
@app.route('/get_total_count')
def get_total_count():
    return jsonify({'total_count': total_count})

# HTML template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic Total Count</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(120deg, #1e3c72, #2a5298);
            color: white;
            overflow:hidden;
            margin: 0;
        }
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background-color: rgba(0, 0, 0, 0.6);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);
        }
        .navbar h1 {
            margin: 0;
            font-size: 1.5em;
            color: #ffcc00;
            text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
        }
        .navbar .logo {
            width: 40px;
            height: 40px;
            background-color: #fff;
            border-radius: 50%;
        }
        .container {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 90vh;
            text-align: center;
        }
        .content {
            max-width: 400px;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        }
        h1 {
            margin: 0;
            font-size: 2.5em;
            color: #ffcc00;
            text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
        }
        span {
            display: block;
            font-size: 4em;
            font-weight: bold;
            margin-top: 10px;
            color: #00ff99;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
        }
    </style>
    <script>
        function updateTotalCount() {
            fetch('/get_total_count')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-count').innerText = data.total_count;
                })
                .catch(error => console.error('Error fetching total count:', error));
        }

        setInterval(updateTotalCount, 1000);
        window.onload = updateTotalCount;
    </script>
</head>
<body>
    <div class="navbar" style="display:flex;align-items:center;justify-content:center;">
        <h1 style="font-size:140px">SCANSORT</h1>
        
    </div>
    <div class="container">
        <div class="content">
            <h1>COUNT</h1>
            <span id="total-count">0</span>
        </div>
    </div>
</body>
</html>
"""

# Start Flask web server in a separate thread
if __name__ == '__main__':
    button_thread = threading.Thread(target=count_button_presses)
    button_thread.daemon = True  # Exit when the main program exits
    button_thread.start()
    app.run(host='0.0.0.0', port=5000)
