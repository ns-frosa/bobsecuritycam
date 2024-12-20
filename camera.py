import cv2
import time
from base_camera import BaseCamera

class Camera(BaseCamera):
    """An emulated camera implementation that streams frames from an MP4 video file."""
    
    def __init__(self):
        self.video = cv2.VideoCapture('video.mp4')
        if not self.video.isOpened():
            raise RuntimeError('Could not start video.')
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.frame_delay = 1.0 / self.fps

    def __del__(self):
        if self.video.isOpened():
            self.video.release()

    @staticmethod
    def frames():
        camera = Camera()
        while True:
            ret, frame = camera.video.read()
            if not ret:
                # Restart the video if it ends
                camera.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            # Encode the frame in JPEG format
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield jpeg.tobytes()
            time.sleep(camera.frame_delay)