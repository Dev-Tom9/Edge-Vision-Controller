import cv2
import numpy as np
from typing import Tuple, Optional
from config.settings import settings


class FramePerceptionEngine:
    """
    Handles local edge-level perception utilizing optimized OpenCV routines.
    Eliminates system latency and cloud costs by pre-filtering static video feeds.
    """
    def __init__(self) -> None:
        self.camera_index: int = settings.CAMERA_INDEX
        self.width: int = settings.FRAME_WIDTH
        self.height: int = settings.FRAME_HEIGHT
        self.motion_threshold: int = settings.MOTION_THRESHOLD
        self.previous_frame: Optional[np.ndarray] = None

    def initialize_camera(self) -> cv2.VideoCapture:
        """Initializes and configures the hardware video capture peripheral."""
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to bind video capture device at index {self.camera_index}")
        
        # Enforce downsampled resolution constraints configured in Settings
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return cap

    def process_and_validate_frame(self, raw_frame: np.ndarray) -> Tuple[bool, bytes]:
        """
        Applies mathematical frame-differencing to detect motion/anomalies.
        Returns a boolean flag indicating if the frame warrants cognitive processing,
        along with the optimized JPEG byte buffer.
        """
        # Convert to grayscale and apply Gaussian blur to eliminate high-frequency sensor noise
        gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.GaussianBlur(gray, (21, 21), 0)

        # Initialize base frame state on first iteration loop
        if self.previous_frame is None:
            self.previous_frame = gray_blurred
            _, encoded_img = cv2.imencode(".jpg", raw_frame)
            return False, encoded_img.tobytes()

        # Compute the absolute delta between current frame and reference frame
        frame_delta = cv2.absdiff(self.previous_frame, gray_blurred)
        threshold_frame = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)

        # Calculate total structural displacement area
        contours, _ = cv2.findContours(threshold_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant_anomaly_detected = False

        for contour in contours:
            if cv2.contourArea(contour) >= self.motion_threshold:
                significant_anomaly_detected = True
                break

        # Dynamic baseline updates to accommodate subtle environmental lighting shifts
        self.previous_frame = gray_blurred

        # Compress native frame to highly optimized JPEG byte-array for payload transport
        _, encoded_img = cv2.imencode(".jpg", raw_frame)
        return significant_anomaly_detected, encoded_img.tobytes()
