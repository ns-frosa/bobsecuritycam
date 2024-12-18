from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
import cv2
import asyncio

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
pcs = set()

# Load the video using OpenCV
video_path = "video.mp4"  # Replace with your video file
cap = cv2.VideoCapture(video_path)

class VideoStreamTrack(MediaStreamTrack):
    kind = "video"

    async def recv(self):
        # Get a single frame from OpenCV
        ret, frame = cap.read()

        # Restart the video if it ends
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()

        # Convert frame to RGB (as required by WebRTC)
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Wrap the frame into an aiortc VideoFrame
        from av import VideoFrame
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts, video_frame.time_base = self.next_timestamp()
        return video_frame


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("offer")
async def handle_offer(data):
    offer = RTCSessionDescription(data["sdp"], data["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    # Add the video track to the connection
    pc.addTrack(VideoStreamTrack())

    # Set remote description
    await pc.setRemoteDescription(offer)

    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Send answer back to the client
    emit("answer", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})


@socketio.on("disconnect")
def disconnect():
    for pc in pcs:
        asyncio.run(pc.close())
    pcs.clear()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001)
