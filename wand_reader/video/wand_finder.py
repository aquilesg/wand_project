import cv2
import numpy as np
import logging
import platform
from typing import Optional, Tuple

logger = logging.getLogger(__name__)
WARMUP_FRAME_COUNT = 100

class Detector():
    def __init__(
        self,
        camera_index: int = 0,
        brightness_threshold: int = 220,
        min_area: float = 10.0,
        max_area: float = 5000.0,
        snapshot_path: Optional[str] = None,
    ):
        self.brightness_threshold = brightness_threshold
        self.min_area = min_area
        self.max_area = max_area
        
        if platform.system() == "Linux":
            pipeline = (
                "libcamerasrc ! "
                "video/x-raw, width=640, height=480 ! "
                "queue ! videoconvert ! queue ! "
                "video/x-raw, format=BGR ! appsink drop=True"
    )
            self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            logger.info("Starting Pi Camera via GStreamer")
        if not self.__check_camera(snapshot_path):
            raise RuntimeError("Camera check failed, aborting.")

    def __enter__(self) -> "Detector":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

    def check_for_wand_spot(self) -> Optional[Tuple[int, int]]:
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, self.brightness_threshold, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if not (self.min_area <= area <= self.max_area):
                continue

            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter ** 2)
            if circularity < 0.5: 
                continue

            M = cv2.moments(contour)
            if M["m00"] == 0: 
                continue
            
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            candidates.append((cx, cy, area))

        if not candidates:
            return None

        best = max(candidates, key=lambda c: c[2])
        return (best[0], best[1])


    def __check_camera(self, snapshot_path: Optional[str] = None) -> bool:
        if not self.cap.isOpened():
            logger.error("Camera is not opened")
            return False

        for _ in range(WARMUP_FRAME_COUNT):
            self.cap.read()
        ret, frame = self.cap.read()
        if not ret or frame is None:
            logger.error("Camera opened but failed to read a frame")
            return False

        h, w = frame.shape[:2]
        logger.info(f"Camera operational — resolution: {w}x{h}")

        if snapshot_path:
            cv2.imwrite(snapshot_path, frame)
            logger.info(f"Startup snapshot saved to: {snapshot_path}")

        return True

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
