# Interactive Audio Effects Controller

A real-time audio effects controller that uses facial tracking to modulate audio effects based on mouth movements. This program allows you to control various audio effects (reverb, filter, and distortion) by simply opening and closing your mouth.

## Features

- Real-time facial tracking using MediaPipe
- Control of three different audio effects:
  - Reverb
  - Low-pass filter
  - Distortion
- Calibration system for personalized mouth movement sensitivity
- Real-time audio processing with PyAudio
- Visual feedback with FPS counter and effect intensity display
- Support for WAV audio files

## Requirements

- Python 3.x
- Webcam
- Audio output device

## Dependencies
opencv-python>=4.5.0

numpy>=1.19.0

pygame>=2.0.0

soundfile>=0.10.0

librosa>=0.8.0

scipy>=1.7.0

pyaudio>=0.2.11

mediapipe


## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the program with a WAV audio file:

```bash
python main.py --audio path/to/your/audio.wav
```

### Command Line Arguments

- `--camera`: Camera device index (default: 0)
- `--width`: Camera capture width (default: 640)
- `--height`: Camera capture height (default: 480)
- `--sensitivity`: Mouth movement sensitivity (default: 1.0)
- `--audio`: Path to the WAV audio file (required)
- `--buffer-size`: Audio buffer size (default: 1024)
- `--effect`: Effect to control (choices: 'reverb', 'filter', 'distortion', default: 'reverb')

### Controls

- `q`: Quit the program
- `p`: Pause/Play audio
- `c`: Enter calibration mode
- `r`: Reset calibration
- `1`: Switch to reverb effect
- `2`: Switch to filter effect
- `3`: Switch to distortion effect

### Calibration

1. Press `c` to start calibration
2. Close your mouth and press `c` again
3. Open your mouth wide and press `c` one more time
4. The program will now be calibrated to your mouth movements

## How It Works

The program uses MediaPipe's face mesh to track facial landmarks, specifically focusing on mouth movements. The degree of mouth opening is mapped to control parameters of the selected audio effect. The audio processing is done in real-time using PyAudio, allowing for immediate response to facial movements.