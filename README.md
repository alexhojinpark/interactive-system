# Interactive Facial Control Systems for Audio Processing

### Project Overview

This project explores the development of musical interactive systems that utilize facial tracking, specifically mouth movements to control audio effects and generate sound. After encountering challenges with my original concept of implementing a Wah Effect MIDI Controller using Csound DSP integrated with a real-time Python webcam application, I pivoted to conduct a series of experimental research implementations. Each research direction explores different aspects of facial control for musical expression, resulting in a portfolio of complementary interactive systems.

# Research Portfolio

## Research 1: Mouth Interactive Audio Effect Controller (Python, DAW, MIDI, real-time)
**Face Tracking to OSC System**

This implementation uses computer vision to track facial movements, particularly mouth opening and closing, and transmits this data via Open Sound Control (OSC) protocol to control audio parameters in digital audio workstations or other OSC-compatible applications.

Technical Features:
- Real-time face tracking using MediaPipe's facial landmark detection
- Calibration system that adapts to individual facial characteristics
- Rate-limited OSC message transmission (configurable up to 30 messages per second)
- Control mapping from continuous mouth movements to OSC values (0-127)
- Integration with DAWs like Reaper through parameter learning

Implementation Details:
- Built with Python 3.10+ using OpenCV and MediaPipe for facial analysis
- Configurable camera settings, sensitivity adjustments, and OSC parameters
- Interactive calibration process that captures closed and open mouth positions
- Visual feedback system with live preview and debug information




## Research 2: Mouth Interactive Audio Effect Controller (Python, Audio Input file)
**Direct Audio Processing System**

This implementation takes a different approach by directly processing audio files in real-time based on facial movements, without requiring external audio software.

Technical Features:
- Three distinct audio effects controlled by mouth movements:
  - Reverb: Adds spatial depth proportional to mouth openness
  - Low-pass filter: Modulates cutoff frequency based on mouth position
  - Distortion: Adjusts distortion amount according to mouth openness
- Real-time audio processing using PyAudio
- Support for WAV audio file playback and processing
- Visual feedback showing effect intensity and mouth position

Implementation Details:
- Audio buffer management for low-latency processing
- Effect parameter mapping optimized for perceptible changes in sound
- Keyboard controls for effect selection and calibration
- FPS counter to monitor performance

Challenges:
While functional, this implementation highlighted some limitations of Python-based audio processing, with distortion effects being the most perceptible while reverb and filtering effects were more subtle.

## Research 3: Interactive Space Ambient Music with Webcam (Pure Data)
**Generative Ambient System**

This implementation explores a more composition-focused approach, using Pure Data (Pd) to create an interactive ambient music generator controlled by webcam input.

Technical Features:
- Webcam-controlled oscillators that respond to movement
- Multiple interconnected patches for ambient sound generation
- Randomized elements that create evolving soundscapes
- Performance-oriented interface design

Implementation Details:
- Built from scratch in Pure Data
- The top-left patch contains webcam-controlled oscillators
- Supporting patches generate complementary ambient elements
- Designed with both compositional and performance applications in mind


## Technical Achievements and Learning Outcomes

**This project required integrating knowledge from multiple domains:**

1. Computer Vision Techniques:
   - Implementation of real-time facial landmark tracking
   - Development of calibration systems for personalized response
   - Optimizing vision processing for low latency

2. Audio Processing:
   - Real-time DSP implementation for multiple effect types
   - Audio buffer management for continuous processing
   - Parameter mapping from continuous control signals to perceptually relevant effect parameters

3. Communication Protocols:
   - OSC message formatting and transmission
   - Rate limiting and optimization for smooth control

4. User Interface Design:
   - Visual feedback systems to indicate control state
   - Multi-modal input combining facial gestures and keyboard commands
   - Intuitive calibration procedures

5. Cross-Platform Integration:
   - Connecting Python tracking systems with DAWs
   - Building standalone processing applications
   - Developing Pure Data patches for custom sound generation
