import cv2
import mediapipe as mp


class HandTracker:
    """Tracks hand using Mediapipe and returns normalized X position"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        self.last_x = 0.5
        
    def get_hand_position(self):
        """Returns normalized X position (0.0-1.0) of index finger tip"""
        success, frame = self.cap.read()
        
        if not success:
            return self.last_x, None
            
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Get index finger tip (landmark 8)
            index_tip = hand_landmarks.landmark[8]
            self.last_x = index_tip.x
            
            # Draw landmarks on frame for debugging
            self.mp_draw.draw_landmarks(
                frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS
            )
        
        # Resize frame for small preview
        small_frame = cv2.resize(frame, (160, 120))
        
        return self.last_x, small_frame
    
    def release(self):
        """Clean up resources"""
        self.cap.release()
        self.hands.close()
