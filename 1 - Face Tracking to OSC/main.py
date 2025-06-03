import cv2
import argparse
import time
from face_tracker import FaceTracker
from osc_sender import OscSender


def parse_arguments():
    parser = argparse.ArgumentParser(description='Facial Mouth Tracking to OSC')
    
    # camera setting
    parser.add_argument('--camera', type=int, default=0,
                        help='Camera device index (default: 0)')
    parser.add_argument('--width', type=int, default=640,
                        help='Camera capture width (default: 640)')
    parser.add_argument('--height', type=int, default=480,
                        help='Camera capture height (default: 480)')
    
    # face track setting
    parser.add_argument('--sensitivity', type=float, default=1.0,
                        help='Mouth detection sensitivity (default: 1.0)')
    parser.add_argument('--detection-confidence', type=float, default=0.5,
                        help='Minimum face detection confidence (default: 0.5)')
    parser.add_argument('--tracking-confidence', type=float, default=0.5,
                        help='Minimum landmark tracking confidence (default: 0.5)')
    
    # OSC setting
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help='OSC server IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                        help='OSC server port (default: 8000)')
    parser.add_argument('--rate-limit', type=int, default=30,
                        help='Maximum OSC messages per second (default: 30)')
    
    # other setting
    parser.add_argument('--no-preview', action='store_true',
                        help='Disable preview window')
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    # reset webcam
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # tracker and OSC sender reset
    face_tracker = FaceTracker(
        sensitivity=args.sensitivity,
        min_detection_confidence=args.detection_confidence,
        min_tracking_confidence=args.tracking_confidence
    )
    
    osc_sender = OscSender(
        ip=args.ip,
        port=args.port,
        rate_limit=args.rate_limit
    )
    
    print(f"Starting mouth tracking to OSC:")
    print(f"  - Camera: {args.camera}")
    print(f"  - OSC Target: {args.ip}:{args.port}")
    print(f"  - Rate Limit: {args.rate_limit} msg/sec")
    print(f"  - Sensitivity: {args.sensitivity}")
    print("Press 'q' to quit, 'c' to calibrate, 'r' to reset calibration")
    
    # calibration
    calibration_mode = False
    calibration_step = 0
    mouth_closed_value = None
    
    # MAIN LOOP
    try:
        while True:
            # Read frame from camera
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break
            
            # Process frame
            processed_frame, mouth_value, success = face_tracker.process_frame(frame)
            
            if calibration_mode:
                if calibration_step == 0:
                    # mouth closed
                    cv2.putText(processed_frame, "Keep mouth CLOSED and press 'c'", 
                                (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif calibration_step == 1:
                    # mouth opened
                    cv2.putText(processed_frame, "Open mouth WIDE and press 'c'", 
                                (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # OSC message send (when face detected)
            if success:
                osc_sender.send_mouth_value(mouth_value)
                
                # Send debug info
                stats = osc_sender.get_statistics()
                msg_rate = stats["messages_per_second"]
                cv2.putText(processed_frame, f"OSC: {args.ip}:{args.port}", 
                            (10, processed_frame.shape[0] - 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(processed_frame, f"Msg Rate: {msg_rate:.1f}/s", 
                            (10, processed_frame.shape[0] - 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Show processed frame
            if not args.no_preview:
                cv2.imshow('Mouth Tracking to OSC', processed_frame)
            
            # Check for key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):  # end program
                break
                
            elif key == ord('c'):  # edit calibration
                if not calibration_mode:
                    # calibration triggered
                    calibration_mode = True
                    calibration_step = 0
                    print("Calibration mode started. Keep mouth closed and press 'c'")
                elif calibration_step == 0 and success:
                    # save closed mouth value
                    mouth_closed_value = mouth_value
                    calibration_step = 1
                    print(f"Closed mouth value: {mouth_closed_value}. Now open mouth wide and press 'c'")
                elif calibration_step == 1 and success:
                    # save open mouth value
                    mouth_open_value = mouth_value
                    face_tracker.calibrate(mouth_closed_value, mouth_open_value)
                    calibration_mode = False
                    print(f"Calibration complete! Range: {mouth_closed_value} - {mouth_open_value}")
                    
            elif key == ord('r'):  # reset calibration
                face_tracker.reset_calibration()
                calibration_mode = False
                print("Calibration reset")
    
    except KeyboardInterrupt:
        print("Program interrupted by user")
    
    finally:
        # Release resources
        cap.release()
        face_tracker.release()
        cv2.destroyAllWindows()
        print("Program terminated")


if __name__ == "__main__":
    main()