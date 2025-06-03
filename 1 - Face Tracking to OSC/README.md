# Interactive Mouth Audio Effect Control

## Face Tracking to OSC

A Python application that tracks facial movements, specifically mouth opening/closing, and sends the data via OSC (Open Sound Control) protocol. This can be useful for controlling audio parameters, visual effects, or other applications that can receive OSC messages.

## Features

- Real-time face tracking using MediaPipe
- Mouth opening/closing detection
- OSC message transmission
- Adjustable sensitivity and calibration
- Live preview with debug information
- Configurable camera settings
- Rate-limited OSC message sending

## Requirements

- Python 3.10 or higher
- Webcam
- Required Python packages (see `requirements.txt`):
  - opencv-python >= 4.5.0
  - mediapipe == 0.10.0
  - numpy >= 1.19.0
  - python-osc >= 1.8.0

## Installation

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv310
   # On Windows:
   .\venv310\Scripts\activate
   # On Unix/MacOS:
   source venv310/bin/activate
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the program with default settings:
```bash
python main.py
```

### Command Line Arguments

- Camera settings:
  - `--camera`: Camera device index (default: 0)
  - `--width`: Camera capture width (default: 640)
  - `--height`: Camera capture height (default: 480)

- Face tracking settings:
  - `--sensitivity`: Mouth detection sensitivity (default: 1.0)
  - `--detection-confidence`: Minimum face detection confidence (default: 0.5)
  - `--tracking-confidence`: Minimum landmark tracking confidence (default: 0.5)

- OSC settings:
  - `--ip`: OSC server IP address (default: 127.0.0.1)
  - `--port`: OSC server port (default: 8000)
  - `--rate-limit`: Maximum OSC messages per second (default: 30)

- Other settings:
  - `--no-preview`: Disable preview window

### Controls

- Press `c` to start calibration
- Press `r` to reset calibration
- Press `q` to quit the program

### Calibration

1. Press `c` to enter calibration mode
2. Keep your mouth closed and press `c` again
3. Open your mouth wide and press `c` one more time
4. The program will now be calibrated to your mouth movements

## OSC Messages

The program sends OSC messages to the specified IP address and port:
- Address: `/mouth`
- Value: Integer between 0-127 representing mouth openness

### Reaper OSC
1. Set reaper to listen to OSC messages
2. Send OSC message to reaper
3. Use `learn` feature in reaper to control parameters with OSC messages