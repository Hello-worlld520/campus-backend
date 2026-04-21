
"""
校园安防后端 - 多模型版（YOLO Pose + LSTM）
"""

from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import cv2
import os
import time
import threading

from config import *
from video_final import VideoActionDetector  # ⭐ 核心改动

# 初始化Flask
app = Flask(__name__)
CORS(app)

# 全局变量
detector = None   # ⭐ 不再是 model
active_processes = {}
process_lock = threading.Lock()


# ====================== 1. 加载模型 ======================
def load_model():
    global detector

    print("\n 检查模型文件...")

    if not os.path.exists(POSE_MODEL_PATH):
        print(f" 找不到 pose 模型: {POSE_MODEL_PATH}")
        return False

    if not os.path.exists(LSTM_MODEL_PATH):
        print(f" 找不到 LSTM 模型: {LSTM_MODEL_PATH}")
        return False

    try:
        print(" 初始化行为识别模型...")
        detector = VideoActionDetector(model_path=LSTM_MODEL_PATH)
        print(" 模型加载成功！")
        return True
    except Exception as e:
        print(f" 模型加载失败: {e}")
        return False


# ====================== 2. 视频流 ======================
def generate_frames(source, source_id, is_file=False):
    global detector

    with process_lock:
        if source_id in active_processes:
            return
        active_processes[source_id] = True

    cap = cv2.VideoCapture(source if not source.isdigit() else int(source))

    if not cap.isOpened():
        print(f" 无法打开视频源: {source}")
        return

    try:
        while active_processes.get(source_id, False):
            success, frame = cap.read()
            if not success:
                break

            #  核心推理（替换 YOLO）
            processed_frame, results = detector.process_frame(frame)

            #  打架检测（根据动作）
            alert = None
            for r in results:
                if r["action"] in ["Slap face", "Kick", "Hit wall"]:
                    alert = f"危险行为: {r['action']}"
                    break

            if alert:
                cv2.rectangle(processed_frame, (10, 10), (500, 80), (0, 0, 255), -1)
                cv2.putText(processed_frame, alert, (20, 55),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

            # 编码输出
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            time.sleep(1 / FPS_LIMIT)

    finally:
        cap.release()
        with process_lock:
            active_processes.pop(source_id, None)


# ====================== 3. API ======================

@app.route('/')
def home():
    return jsonify({
        "name": "校园安防后端（多模型版）",
        "model_loaded": detector is not None
    })


@app.route('/video_feed')
def video_feed():
    source = request.args.get('source', '0')
    source_id = f"stream_{source}"

    if source_id in active_processes:
        active_processes[source_id] = False
        time.sleep(0.5)

    return Response(
        generate_frames(source, source_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/stop_all')
def stop_all():
    for k in list(active_processes.keys()):
        active_processes[k] = False
    return jsonify({"msg": "stopped"})


# ====================== 4. 启动 ======================
if __name__ == '__main__':
    print(" 启动后端...")

    if load_model():
        print(f"🌐 http://127.0.0.1:{PORT}")
        app.run(host=HOST, port=PORT, threaded=True)
    else:
        print(" 启动失败")
