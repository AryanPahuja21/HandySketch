from flask import Flask, Response, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, emit, SocketIO
import random
from string import ascii_uppercase

from canvas import gen_frames

app = Flask(__name__)
app.config["SECRET_KEY"] = "hshshsajlk"
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code


@app.route("/")
def home():
    return render_template("home.html")


@app.route('/room', methods=['POST', 'GET'])
def room():
    session.clear()
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template('room.html', error='Please enter a name', code=code, name=name)
        
        if join!=False and not code:
            return render_template('room.html', error='Please enter a room code',code=code, name=name)
        
        room = code
        if create!=False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0}
        elif code not in rooms:
            return render_template('room.html', error='Room does not exist', code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for('sketchRoom'))

    return render_template('room.html')

@app.route('/sketchRoom')
def sketchRoom():
    room = session.get('room')
    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('room'))
    
    return render_template('sketchRoom.html')

@app.route('/sketch')
def sketch():
    return render_template('sketchRoom.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    socketio.run(app, debug=True)
