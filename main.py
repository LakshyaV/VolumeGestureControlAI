import cv2
import mediapipe as mp
import subprocess

def find_hands(img, mode=False, max_hands=2, model_c=1, detection_con=0.5, track_con=0.5, draw=True):
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    hands = mp_hands.Hands(mode, max_hands, model_c, detection_con, track_con)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks and draw:
        for hand_land in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_land, mp_hands.HAND_CONNECTIONS)

    return img, result

def find_position(img, result, hand_no=0, draw=True):
    pos_list = []
    if result.multi_hand_landmarks:
        my_hand = result.multi_hand_landmarks[hand_no]
        for id, lm in enumerate(my_hand.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            pos_list.append([id, cx, cy])

            if draw:
                cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)

    return pos_list

def change_volume(hand_direction):

    if hand_direction == "up":
        subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
    elif hand_direction == "down":
        subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])

def draw_volume_bar(img, volume):
    bar_width = 400
    bar_height = 20
    bar_x = int((img.shape[1] - bar_width) / 2)
    bar_y = 50

    cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (0, 0, 0), 2)
    filled_width = int(volume / 100 * bar_width)
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f"Volume: {volume}", (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

def main():
    cap = cv2.VideoCapture(0)
    width = 700
    height = 350
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    while True:
        success, img = cap.read()
        img, result = find_hands(img)
        pos_list = find_position(img, result)

        if len(pos_list) != 0:

            tip_x, tip_y = pos_list[4][1], pos_list[4][2]

            wrist_x, wrist_y = pos_list[0][1], pos_list[0][2]

            if tip_y < wrist_y:
                change_volume("up")
            else:
                change_volume("down")


        output = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"], capture_output=True, text=True)
        volume = int(output.stdout.strip())

        draw_volume_bar(img, volume)

        cv2.imshow("Webcam", img)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
