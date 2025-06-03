import cv2
import numpy as np
import time
import argparse
import pygame
import soundfile as sf
import librosa
import threading
import queue
from face_tracker import FaceTracker
from scipy.signal import lfilter
import pyaudio
import wave
import numpy as np
from queue import Queue
from threading import Thread, Event

class AudioProcessor:
    """processes audio files and applies real-time effects"""
    
    def __init__(self, audio_file, buffer_size=1024, sample_rate=44100):
        """
        Parameters:
            audio_file (str)
            buffer_size (int)
            sample_rate (int)
        """
        self.audio_file = audio_file
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        
        self.audio_data, self.sample_rate = sf.read(audio_file)
        
        if len(self.audio_data.shape) > 1 and self.audio_data.shape[1] > 1:
            self.audio_data = np.mean(self.audio_data, axis=1)
        
        self.reverb_amount = 0.0
        self.filter_cutoff = 0.5
        self.distortion_amount = 0.0
        
        self.audio_queue = Queue()
        self.stop_event = Event()
        self.is_playing = False
        self.current_position = 0
        
        self.p = pyaudio.PyAudio()
        self.stream = None
        
    def set_reverb(self, amount):
        self.reverb_amount = np.clip(amount, 0.0, 1.0)
        
    def set_filter_cutoff(self, amount):
        self.filter_cutoff = np.clip(amount, 0.0, 1.0)
        
    def set_distortion(self, amount):
        self.distortion_amount = np.clip(amount, 0.0, 1.0)
    
    def apply_reverb(self, audio_chunk):
        if self.reverb_amount <= 0:
            return audio_chunk
        
        delay_samples = int(self.sample_rate * 0.1 * self.reverb_amount)
        if delay_samples <= 0:
            return audio_chunk
        
        decay = 0.6 * self.reverb_amount
        
        delayed = np.zeros_like(audio_chunk)
        if delay_samples < len(audio_chunk):
            delayed[delay_samples:] = audio_chunk[:-delay_samples] * decay
        
        return audio_chunk + delayed
    
    def apply_lowpass_filter(self, audio_chunk):
        if self.filter_cutoff >= 1.0:
            return audio_chunk
        
        cutoff = 0.1 + 0.8 * self.filter_cutoff
        b = [1 - cutoff]
        a = [1, -cutoff]
        return lfilter(b, a, audio_chunk)
    
    def apply_distortion(self, audio_chunk):
        if self.distortion_amount <= 0:
            return audio_chunk
        
        gain = 1.0 + 4.0 * self.distortion_amount
        return np.tanh(audio_chunk * gain) / gain
    
    def process_audio(self, audio_chunk):
        processed = audio_chunk.copy()
        
        processed = self.apply_lowpass_filter(processed)
        
        processed = self.apply_distortion(processed)
        
        processed = self.apply_reverb(processed)
        
        if np.max(np.abs(processed)) > 0:
            processed = processed / np.max(np.abs(processed))
        
        return processed
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        if self.stop_event.is_set():
            return (None, pyaudio.paComplete)
        
        if self.current_position + frame_count < len(self.audio_data):
            audio_chunk = self.audio_data[self.current_position:self.current_position + frame_count]
            self.current_position += frame_count
        else:
            remaining = len(self.audio_data) - self.current_position
            audio_chunk = np.zeros(frame_count)
            if remaining > 0:
                audio_chunk[:remaining] = self.audio_data[self.current_position:]
            self.current_position = 0
        
        processed = self.process_audio(audio_chunk)

        out_data = (processed * 32767).astype(np.int16).tobytes()
        
        return (out_data, pyaudio.paContinue)
    
    def play(self):
        if self.is_playing:
            return
        
        self.is_playing = True
        self.stop_event.clear()
        self.current_position = 0
        
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.buffer_size,
            stream_callback=self._audio_callback
        )
        
        self.stream.start_stream()
    
    def stop(self):
        if not self.is_playing:
            return
        
        self.stop_event.set()
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        self.is_playing = False
    
    def release(self):
        self.stop()
        if self.p:
            self.p.terminate()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Control audio effects with mouth shape')
    

    parser.add_argument('--camera', type=int, default=0,
                        help='Camera device index (default: 0)')
    parser.add_argument('--width', type=int, default=640,
                        help='camera capture height (default: 640)')
    parser.add_argument('--height', type=int, default=480,
                        help='Camera capture width (default: 640)')

    parser.add_argument('--sensitivity', type=float, default=1.0,
                        help='Mouth Sensitivity (default: 1.0)')   

    parser.add_argument('--audio', type=str, required=True,
                        help='Audio file path to be processed (.wav file)')
    parser.add_argument('--buffer-size', type=int, default=1024,
                        help='Audio buffer size (default: 1024)')
    
    parser.add_argument('--effect', type=str, default='reverb',
                        choices=['reverb', 'filter', 'distortion'],
                        help='control the shape (default: Reverb)')
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    
    if not cap.isOpened():
        print("Error: Cannot open camera.")
        return
    
    face_tracker = FaceTracker(
        sensitivity=args.sensitivity,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    try:
        audio_processor = AudioProcessor(
            audio_file=args.audio,
            buffer_size=args.buffer_size
        )
    except Exception as e:
        print(f"Error: cannot load audio: {e}")
        cap.release()
        return
    
    print(f"CONTROL {args.effect} WITH YOUR MOUTH:")
    print(f"  - CAMERA: {args.camera}")
    print(f"  - AUDIO FILE: {args.audio}")
    print(f"  - EFFECT MODE: {args.effect}")
    print("'q' for quit program, 'p'for audio pause/play, 'r' for reset calibration")
    
    calibration_mode = False
    calibration_step = 0
    mouth_closed_value = None
    
    audio_processor.play()
    is_paused = False
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: cannot read frame.")
                break
            
            processed_frame, mouth_value, success = face_tracker.process_frame(frame)
            
            if calibration_mode:
                if calibration_step == 0:
                    cv2.putText(processed_frame, "Close your mouth and press 'c'", 
                                (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif calibration_step == 1:
                    cv2.putText(processed_frame, "Open your mouth wide and press 'c'", 
                                (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            if success:
                normalized_value = mouth_value / 127.0
                
                if args.effect == 'reverb':
                    audio_processor.set_reverb(normalized_value)
                    effect_name = "reverb"
                elif args.effect == 'filter':
                    audio_processor.set_filter_cutoff(normalized_value)
                    effect_name = "filter"
                elif args.effect == 'distortion':
                    audio_processor.set_distortion(normalized_value)
                    effect_name = "distortion"
                
                cv2.putText(processed_frame, f"{effect_name}: {normalized_value:.2f}", 
                            (10, processed_frame.shape[0] - 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            status = "pause" if is_paused else "playing"
            cv2.putText(processed_frame, f"Status: {status}", 
                        (10, processed_frame.shape[0] - 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Control Audio Effects with your mouth', processed_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
                
            elif key == ord('p'): 
                if is_paused:
                    audio_processor.play()
                    is_paused = False
                else:
                    audio_processor.stop()
                    is_paused = True
                    
            elif key == ord('c'):  
                if not calibration_mode:
                    calibration_mode = True
                    calibration_step = 0
                    print("Calibration Starting, Close your mouth and press 'c'.")
                elif calibration_step == 0 and success:
                    mouth_closed_value = mouth_value
                    calibration_step = 1
                    print(f"Mouth Closed Value: {mouth_closed_value}. Now open your mouth and press 'c'.")
                elif calibration_step == 1 and success:
                    mouth_open_value = mouth_value
                    face_tracker.calibrate(mouth_closed_value, mouth_open_value)
                    calibration_mode = False
                    print(f"Calibration Edited: {mouth_closed_value} - {mouth_open_value}")
                    
            elif key == ord('r'):
                face_tracker.reset_calibration()
                calibration_mode = False
                print("Calibration reset.")
                
            elif key in [ord('1'), ord('2'), ord('3')]:
                if key == ord('1'):
                    args.effect = 'reverb'
                elif key == ord('2'):
                    args.effect = 'filter'
                elif key == ord('3'):
                    args.effect = 'distortion'
                print(f"Effect Changed to : '{args.effect}'.")
    
    except KeyboardInterrupt:
        print("quit program.")
    
    finally:
        audio_processor.release()
        cap.release()
        face_tracker.release()
        cv2.destroyAllWindows()
        print("program finished.")


if __name__ == "__main__":
    main()
