from flask import Flask, render_template, Response
import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import math

app = Flask(__name__)

blue_points = [deque(maxlen=1024)]
green_points = [deque(maxlen=1024)]
red_points = [deque(maxlen=1024)]
yellow_points = [deque(maxlen=1024)]

blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0

kernel = np.ones((5,5), np.uint8)

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
color_index = 0

paint_window = np.zeros((471, 636, 3), dtype=np.uint8) + 255

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
ret = True

def gen_frames():
    global ret, blue_points, green_points, red_points, yellow_points, blue_index, green_index, red_index, yellow_index, color_index, paint_window
    while True:
        ret, frame = cap.read()

        x, y, c = frame.shape

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            landmarks = []
            for hand_landmarks in result.multi_hand_landmarks:
                for lm in hand_landmarks.landmark:
                    lmx = int(lm.x * 640)
                    lmy = int(lm.y * 480)
                    landmarks.append([lmx, lmy])

                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fore_finger = (landmarks[8][0], landmarks[8][1])
            center = fore_finger
            thumb = (landmarks[4][0], landmarks[4][1])

            # Draw rectangles for color selection
            paint_window = cv2.rectangle(paint_window, (40,1), (140,65), (0,0,0), 2)
            paint_window = cv2.rectangle(paint_window, (160,1), (255,65), (255,0,0), 2)
            paint_window = cv2.rectangle(paint_window, (275,1), (370,65), (0,255,0), 2)
            paint_window = cv2.rectangle(paint_window, (390,1), (485,65), (0,0,255), 2)
            paint_window = cv2.rectangle(paint_window, (505,1), (600,65), (0,255,255), 2)

            cv2.putText(paint_window, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(paint_window, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(paint_window, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(paint_window, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(paint_window, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)

            if (thumb[1] - center[1] < 30):
                blue_points.append(deque(maxlen=512))
                blue_index += 1
                green_points.append(deque(maxlen=512))
                green_index += 1
                red_points.append(deque(maxlen=512))
                red_index += 1
                yellow_points.append(deque(maxlen=512))
                yellow_index += 1

            elif center[1] <= 65:
                if 40 <= center[0] <= 140:
                    blue_points = [deque(maxlen=512)]
                    green_points = [deque(maxlen=512)]
                    red_points = [deque(maxlen=512)]
                    yellow_points = [deque(maxlen=512)]

                    blue_index = 0
                    green_index = 0
                    red_index = 0
                    yellow_index = 0

                    paint_window[67:, :, :] = 255
                elif 160 <= center[0] <= 255:
                    color_index = 0  # Blue
                elif 275 <= center[0] <= 370:
                    color_index = 1  # Green
                elif 390 <= center[0] <= 485:
                    color_index = 2  # Red
                elif 505 <= center[0] <= 600:
                    color_index = 3  # Yellow
            else:
                if color_index == 0:
                    blue_points[blue_index].appendleft(center)
                elif color_index == 1:
                    green_points[green_index].appendleft(center)
                elif color_index == 2:
                    red_points[red_index].appendleft(center)
                elif color_index == 3:
                    yellow_points[yellow_index].appendleft(center)

                distance = math.sqrt((thumb[0] - fore_finger[0]) ** 2 + (thumb[1] - fore_finger[1]) ** 2)
                thickness = int(distance / 20)
                if thickness < 1:
                    thickness = 1

        else:
            blue_points.append(deque(maxlen=512))
            blue_index += 1
            green_points.append(deque(maxlen=512))
            green_index += 1
            red_points.append(deque(maxlen=512))
            red_index += 1
            yellow_points.append(deque(maxlen=512))
            yellow_index += 1

        points = [blue_points, green_points, red_points, yellow_points]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], thickness)
                    cv2.line(paint_window, points[i][j][k - 1], points[i][j][k], colors[i], thickness)

        ret, buffer = cv2.imencode('.jpg', paint_window)
        paint_window_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + paint_window_bytes + b'\r\n')

        cv2.waitKey(1)


if __name__ == "__main__":
    app.run()
