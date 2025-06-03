import cv2
import mediapipe as mp
import numpy as np
import time

class FaceTracker:
    def __init__(self, sensitivity=1.0, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Classes that detect face tracking and degree of mouth opening

        Parameters:
            sensitivity (float): open mouth sensitivity (the higher the sensitivity, the more sensitive it is)
            min_detection_confidence (float): Mediapipe Face Detection Reliability Threshold
            min_tracking_confidence (float): Mediapipe landmark tracking reliability threshold
        """
        self.sensitivity = sensitivity
        
        # MediaPipe Face Mesh Reset
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.upper_lip_indices = [13] 
        self.lower_lip_indices = [14]  
        
       
        self.mouth_open_calibration = None
        self.mouth_closed_calibration = None
        self.last_mouth_value = 0
        self.is_calibrated = False
        
        self.last_process_time = time.time()
        self.frame_count = 0
        self.fps = 0
    
    def calibrate(self, mouth_closed_value, mouth_open_value):
        """
        Method to calibrate the minimum/maximum value of the degree of mouth opening

        Parameters:
            mouth_closed_value (float): y-coordinate difference when closed
            mouth_open_value (float): y-coordinate difference when mouth is open to the maximum
        """
        self.mouth_closed_calibration = mouth_closed_value
        self.mouth_open_calibration = mouth_open_value
        self.is_calibrated = True
        
    def reset_calibration(self):
        self.mouth_closed_calibration = None
        self.mouth_open_calibration = None
        self.is_calibrated = False
    
    def process_frame(self, frame):
        """
        Process video frames to calculate the degree of mouth opening

        Parameters:
            frame: Video frame to be processed (in BGR format)

        Returns:
            processed_frame: frame with debug information added
            mouth_value: degree of mouth opening (0-127)
            success: face detection successful
        """
        start_time = time.time()
        self.frame_count += 1
        
        if self.frame_count % 10 == 0:
            current_time = time.time()
            self.fps = 10 / (current_time - self.last_process_time)
            self.last_process_time = current_time
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        results = self.face_mesh.process(frame_rgb)
        
        processed_frame = frame.copy()
        
        mouth_value = self.last_mouth_value
        success = False
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            upper_lip_y = np.mean([face_landmarks.landmark[idx].y for idx in self.upper_lip_indices]) * h
            lower_lip_y = np.mean([face_landmarks.landmark[idx].y for idx in self.lower_lip_indices]) * h
            
            mouth_gap = lower_lip_y - upper_lip_y
            
            if self.is_calibrated:
                min_gap = self.mouth_closed_calibration
                max_gap = self.mouth_open_calibration
            else:
                min_gap = 10
                max_gap = 50
            
            adjusted_gap = mouth_gap * self.sensitivity
            mapped_value = np.interp(adjusted_gap, [min_gap, max_gap], [0, 127])
            mouth_value = int(np.clip(mapped_value, 0, 127))
            self.last_mouth_value = mouth_value
            success = True
            
            self._draw_debug_info(processed_frame, face_landmarks, mouth_value, mouth_gap)
        
        cv2.putText(processed_frame, f"FPS: {self.fps:.1f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(processed_frame, f"Mouth: {mouth_value}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return processed_frame, mouth_value, success
    
    def _draw_debug_info(self, frame, face_landmarks, mouth_value, mouth_gap):

        self.mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
        )
        
        self.mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_LIPS,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
        )
        
        h, w, _ = frame.shape
        for idx in self.upper_lip_indices + self.lower_lip_indices:
            pos = face_landmarks.landmark[idx]
            cx, cy = int(pos.x * w), int(pos.y * h)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        
        bar_x, bar_y = w - 50, 50
        bar_height = 200
        bar_width = 30
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     (100, 100, 100), -1)
        
        value_height = int((mouth_value / 127) * bar_height)
        cv2.rectangle(frame, (bar_x, bar_y + bar_height - value_height), 
                     (bar_x + bar_width, bar_y + bar_height), (0, 255, 0), -1)
        
        cv2.putText(frame, f"Gap: {mouth_gap:.1f}", (w - 150, bar_y + bar_height + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def release(self):
        self.face_mesh.close()