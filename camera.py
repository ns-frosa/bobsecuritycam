import cv2
import time

class Camera:
    """An emulated camera implementation that streams frames from an MP4 video file over UDP."""
    
    def __init__(self):
        self.video = cv2.VideoCapture('video.mp4')
        if not self.video.isOpened():
            raise RuntimeError('Could not start video.')
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.frame_delay = 1.0 / self.fps

        # GStreamer pipeline for UDP streaming
        self.pipeline = (
            'appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! '
            'rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5001'
        )
        self.out = cv2.VideoWriter(self.pipeline, cv2.CAP_GSTREAMER, 0, self.fps, (int(self.video.get(3)), int(self.video.get(4))))

    def __del__(self):
        if self.video.isOpened():
            self.video.release()
        if self.out.isOpened():
            self.out.release()

    def frames(self):
        while True:
            ret, frame = self.video.read()
            if not ret:
                # Restart the video if it ends
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield jpeg.tobytes()
            time.sleep(self.frame_delay)

    def stream(self):
        while True:
            ret, frame = self.video.read()
            if not ret:
                # Restart the video if it ends
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            self.out.write(frame)
            time.sleep(self.frame_delay)

if __name__ == '__main__':
    camera = Camera()
    try:
        camera.stream()
    except KeyboardInterrupt:
        pass