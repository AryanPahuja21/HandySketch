from flask import Flask, Response, render_template, request, session, redirect
from flask_socketio import join_room, leave_room, send, emit, SocketIO
import random
from string import ascii_uppercase

from canvas import gen_frames

app = Flask(__name__)
app.config["SECRET_KEY"] = "hshshsajlk"
socketio = SocketIO(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/sketch')
def paint_canvas():
    return render_template('sketchPage.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    socketio.run(app, debug=True)
