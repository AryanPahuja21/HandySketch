from flask import Flask, Response, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, emit, SocketIO
import random
from string import ascii_uppercase

from canvas import gen_frames

app = Flask(__name__)
app.config["SECRET_KEY"] = "hshshsajlk"
socketio = SocketIO(app)

joins = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in joins:
            break

    return code


@app.route("/")
def home():
    image_url = "/static/assets/heroImage.jpg"
    return render_template("home.html", image_url=image_url)


@app.route('/join', methods=['POST', 'GET'])
def join():
    session.clear()
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template('join.html', error='Please enter a name', code=code, name=name)
        
        if join!=False and not code:
            return render_template('join.html', error='Please enter a join code',code=code, name=name)
        
        join = code
        if create!=False:
            join = generate_unique_code(4)
            joins[join] = {"members": 0}
        elif code not in joins:
            return render_template('join.html', error='Room does not exist', code=code, name=name)
        
        session["join"] = join
        session["name"] = name
        return redirect(url_for('room'))

    return render_template('join.html')

@app.route('/room')
def room():
    join = session.get('join')
    if join is None or session.get('name') is None or join not in joins:
        return redirect(url_for('join'))
    
    return render_template('room.html', code=join)

@app.route('/sketch')
def sketch():
    return render_template('sketch.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on("connect")
def connect(auth):
    join = session.get("join")
    name = session.get("name")
    if not join or not name:
        print("User not authenticated")
        return
    if join not in joins:
        print("Room does not exist")
        leave_room(join)
        return

    join_room(join)
    send(f"{name} has entered the room", to=join)
    joins[join]["members"] += 1
    print(f"{name} has joined the room {join}")

@socketio.on("disconnect")
def disconnect():
    join = session.get("join")
    name = session.get("name")
    leave_room(join)

    if join in joins:
        joins[join]["members"] -= 1
        if joins[join]["members"] <= 0:
            del joins[join]
    
    send({"name": name, "message": "has left the room"}, to=join)
    print(f"{name} has left the room {join}")
    
if __name__ == "__main__":
    socketio.run(app, debug=True)
