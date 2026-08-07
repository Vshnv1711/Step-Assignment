import cv2
import serial
import serial.tools.list_ports
import time
import numpy as np

# ── Arduino Connection ────────────────────────────────────────────────────────
def connect_arduino():
    try:
        s = serial.Serial('COM5', 9600, timeout=1)
        print("✓ Connected to Arduino on COM5")
        return s
    except serial.SerialException:
        pass

    for p in serial.tools.list_ports.comports():
        print(f"Scanning: {p.device} - {p.description}")
        if any(x in p.description for x in ['Arduino', 'USB Serial', 'CH340', 'CP210']):
            try:
                s = serial.Serial(p.device, 9600, timeout=1)
                print(f"✓ Connected to Arduino on {p.device}")
                return s
            except serial.SerialException:
                continue

    print("⚠ No Arduino found — running in preview mode")
    return None

arduino = connect_arduino()
time.sleep(2)

# ── Webcam Connection ─────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Webcam not found on index 0, trying index 1...")
    cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("❌ No webcam found. Please check your camera connection.")
    if arduino:
        arduino.close()
    exit()
print("✓ Webcam opened successfully")

last_gesture = ""
last_time    = 0
COOLDOWN     = 1.5

# ── Skin Detection ────────────────────────────────────────────────────────────
def get_skin_mask(frame):
    hsv   = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 20, 70],    dtype=np.uint8)
    upper = np.array([20, 255, 255], dtype=np.uint8)
    mask  = cv2.inRange(hsv, lower, upper)
    kernel = np.ones((5, 5), np.uint8)
    mask   = cv2.dilate(mask, kernel, iterations=2)
    mask   = cv2.GaussianBlur(mask, (5, 5), 100)
    return mask

# ── Finger Counting (FIXED) ───────────────────────────────────────────────────
def count_fingers_from_contour(contour, frame_area):
    hull    = cv2.convexHull(contour, returnPoints=False)
    defects = cv2.convexityDefects(contour, hull)

    # No defects = fist = 0 fingers
    if defects is None:
        return 0

    finger_count = 0
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(contour[s][0])
        end   = tuple(contour[e][0])
        far   = tuple(contour[f][0])

        a = np.linalg.norm(np.array(end) - np.array(start))
        b = np.linalg.norm(np.array(far) - np.array(start))
        c = np.linalg.norm(np.array(end) - np.array(far))

        if b * c == 0:
            continue

        cos_angle = (b**2 + c**2 - a**2) / (2 * b * c)
        cos_angle = np.clip(cos_angle, -1, 1)
        angle     = np.degrees(np.arccos(cos_angle))

        # Lowered threshold to 8000 for better fist detection
        if angle < 90 and d > 8000:
            finger_count += 1

    # Key fix: 0 gaps = fist, don't add 1
    if finger_count == 0:
        return 0
    return min(finger_count + 1, 5)

# ── Gesture Detection ─────────────────────────────────────────────────────────
def detect_gesture(contour, finger_count, frame_w):
    if finger_count >= 5:
        return 'U'   # Open hand → UP / RED

    if finger_count == 0:
        return 'D'   # Fist → DOWN / GREEN

    if finger_count == 1:
        M = cv2.moments(contour)
        if M["m00"] == 0:
            return 'L'
        cx = int(M["m10"] / M["m00"])
        if cx < frame_w * 0.35 or cx > frame_w * 0.65:
            return 'N'   # Thumb → NEAR / BLINK
        return 'L'       # Index finger → LEFT / YELLOW

    if finger_count == 2:
        return 'R'   # Two fingers → RIGHT / YELLOW

    return None

GESTURE_LABELS = {
    'U': 'UP    -> RED',
    'D': 'DOWN  -> GREEN',
    'L': 'LEFT  -> YELLOW',
    'R': 'RIGHT -> YELLOW',
    'N': 'NEAR  -> BLINK',
}

print("Webcam gesture control started. Press Q to quit.")
print("Gestures:")
print("  Open hand (5 fingers) = UP    → RED")
print("  Fist      (0 fingers) = DOWN  → GREEN")
print("  1 finger  (index)     = LEFT  → YELLOW")
print("  2 fingers             = RIGHT → YELLOW")
print("  Thumb only            = NEAR  → BLINK ALL")
print("Ensure good lighting and plain background for best results.")

# ── Main Loop ─────────────────────────────────────────────────────────────────
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame from webcam.")
            break

        frame            = cv2.flip(frame, 1)
        frame_h, frame_w = frame.shape[:2]

        # ROI — center strip of frame
        roi  = frame[50:frame_h-50, frame_w//4 : frame_w*3//4]
        mask = get_skin_mask(roi)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        gesture_label = "No hand"
        gesture       = None

        if contours:
            max_cnt = max(contours, key=cv2.contourArea)

            if cv2.contourArea(max_cnt) > 8000:
                cv2.drawContours(roi, [max_cnt], -1, (0, 255, 0), 2)

                hull_pts = cv2.convexHull(max_cnt)
                cv2.drawContours(roi, [hull_pts], -1, (255, 0, 0), 2)

                finger_count = count_fingers_from_contour(max_cnt, frame_w)
                gesture      = detect_gesture(max_cnt, finger_count, frame_w // 2)

                # Show finger count on screen for debugging
                cv2.putText(frame, f"Fingers: {finger_count}",
                            (10, 80), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (255, 255, 0), 2)

                if gesture:
                    gesture_label = GESTURE_LABELS.get(gesture, '?')
                    now = time.time()
                    if gesture != last_gesture or (now - last_time) > COOLDOWN:
                        if arduino:
                            arduino.write(gesture.encode())
                        print(f"Sent: {gesture} ({gesture_label})")
                        last_gesture = gesture
                        last_time    = now

        # ── Display ───────────────────────────────────────────────────────────
        frame[50:frame_h-50, frame_w//4 : frame_w*3//4] = roi
        cv2.rectangle(frame, (frame_w//4, 50),
                      (frame_w*3//4, frame_h-50), (200, 200, 0), 2)
        cv2.putText(frame, f"Gesture: {gesture_label}",
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Skin mask preview (top-left corner)
        mask_display = cv2.resize(mask, (frame_w//4, frame_h//4))
        frame[10:10+mask_display.shape[0], 10:10+mask_display.shape[1]] = \
            cv2.cvtColor(mask_display, cv2.COLOR_GRAY2BGR)

        cv2.imshow("Gesture Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    if arduino:
        arduino.close()
    cv2.destroyAllWindows()
    print("✓ Cleanup done.")