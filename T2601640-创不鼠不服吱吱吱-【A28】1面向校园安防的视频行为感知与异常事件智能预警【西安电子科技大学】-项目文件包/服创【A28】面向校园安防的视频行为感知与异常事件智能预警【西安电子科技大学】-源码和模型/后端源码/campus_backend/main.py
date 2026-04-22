# -*- coding: utf-8 -*-
"""
校园安防后端 - 任务制版本（增强版）
保留实时流 /video_feed
上传视频改为：上传 -> 创建任务 -> 后台处理 -> ffmpeg转码 -> 查询进度 -> 播放结果
"""

from flask import Flask, Response, request, jsonify, send_file
from flask_cors import CORS
import cv2
import os
import time
import threading
import logging
import subprocess
import re
from logging.handlers import RotatingFileHandler
from werkzeug.utils import secure_filename

# ====================== [修改点 1] 模型导入 ======================
# 旧: from ultralytics import YOLO
# 新: 导入新的 VideoActionDetector，并引入 analyze_frame 帧处理函数
from video_action_detector import VideoActionDetector  # 替换为新模型模块
from config import *

# ====================== 日志配置 ======================
def setup_logger():
    """配置日志系统"""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('CampusSecurity')
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    detailed_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        'logs/campus_security.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)

    alert_handler = RotatingFileHandler(
        'logs/alert.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    alert_handler.setLevel(logging.WARNING)
    alert_handler.setFormatter(detailed_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(alert_handler)

    return logger


logger = setup_logger()

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH_MB * 1024 * 1024

# ====================== 全局变量 ======================

detector = None

# 实时流状态（摄像头 / RTSP）
active_processes = {}
process_lock = threading.Lock()
stream_alerts = {}

# 上传任务状态（长视频）
tasks = {}
tasks_lock = threading.Lock()


# ====================== 1. 加载模型 ======================
def load_model():
    """加载 POSE+LSTM 模型"""
    # [修改点 3] 模型加载逻辑
    # 旧: global model; 检查 MODEL_PATH; model = YOLO(MODEL_PATH)
    # 新: global detector; 检查 POSE_MODEL_PATH 和 LSTM_MODEL_PATH; detector = VideoActionDetector(...)
    global detector

    logger.info("=" * 50)
    logger.info("Checking model files...")

    # 检查 POSE 模型文件
    if not os.path.exists(POSE_MODEL_PATH):
        logger.error(f"POSE model file not found at: {POSE_MODEL_PATH}")
        logger.info("Solutions:")
        logger.info("  1. Place pose model in models/ folder")
        logger.info("  2. Update POSE_MODEL_PATH in config.py")
        return False

    # 检查 LSTM 模型文件
    if not os.path.exists(LSTM_MODEL_PATH):
        logger.error(f"LSTM model file not found at: {LSTM_MODEL_PATH}")
        logger.info("Solutions:")
        logger.info("  1. Place LSTM model in models/ folder")
        logger.info("  2. Update LSTM_MODEL_PATH in config.py")
        return False

    try:
        logger.info(f"Loading POSE model: {POSE_MODEL_PATH}")
        logger.info(f"Loading LSTM model: {LSTM_MODEL_PATH}")
        detector = VideoActionDetector(
            model_path=LSTM_MODEL_PATH,
            pose_model_path=POSE_MODEL_PATH
        )
        logger.info("Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}", exc_info=True)
        return False

def normalize_alert_label(alert):
    if not alert:
        return ""

    mapping = {
        "fight": "打架",
        "fall": "跌倒",
        "climb": "翻墙",
        "climbing": "翻墙",
        "other": "其他",
        "unknown": "其他"
    }

    key = str(alert).strip()
    return mapping.get(key.lower(), key)

# ====================== 2. 行为分析函数（保留兼容旧接口，内部已不再使用）======================
# 注意：analyze_behavior 已被 analyze_frame 替代，此函数保留仅作向后兼容
def analyze_behavior(results):
    """
    [已废弃] 原 YOLO 行为分析函数，保留作兼容备用。
    新代码中请直接使用 analyze_frame(frame)。
    """
    detections = []
    alert = None
    persons = []

    for r in results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            if conf < CONF_THRESHOLD:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # 使用 detector.names 兼容新模型（若新模型无此属性则跳过）
            class_name = getattr(detector, 'names', {}).get(cls_id, str(cls_id))

            detections.append({
                "class": class_name,
                "confidence": round(conf, 3),
                "bbox": [x1, y1, x2, y2]
            })

            if class_name == "person":
                persons.append({
                    "center": ((x1 + x2) // 2, (y1 + y2) // 2),
                    "bbox": [x1, y1, x2, y2]
                })

    if len(persons) >= 2:
        for i in range(len(persons)):
            for j in range(i + 1, len(persons)):
                dx = persons[i]["center"][0] - persons[j]["center"][0]
                dy = persons[i]["center"][1] - persons[j]["center"][1]
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance < 150:
                    alert = "Fight detected!"
                    logger.warning(f"Fight detected - distance: {distance:.2f}px")
                    break
            if alert:
                break

    return detections, alert


# ====================== 3. ffmpeg 转码 ======================
def transcode_to_browser_mp4(input_path, output_path):
    """
    使用 ffmpeg 转成浏览器更兼容的 mp4(H.264)
    需要系统已安装 ffmpeg
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ]

    logger.info(f"Start ffmpeg transcode: {input_path} -> {output_path}")
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        logger.error(f"ffmpeg transcode failed: {result.stderr}")
        raise Exception(f"ffmpeg transcode failed: {result.stderr}")

    logger.info("ffmpeg transcode completed successfully")


def log_result_event(
    event_type,
    task_id=None,
    source_id=None,
    frame_count=None,
    alert_count=None,
    detections=None,
    extra=None
):
    """
    统一写识别结果事件日志，方便前端展示。
    [修改点 4] 统计逻辑兼容新模型动作列表：
    - 旧: 遍历 r.boxes，根据 cls_id 统计 person_count 和 max_confidence
    - 新: 遍历 detections 动作字典，用 action 字段判断是否为 person
    """
    detections = detections or []
    extra = extra or {}

    # 新模型动作字典格式：{"action": "fight", "confidence": 0.95, ...}
    # 兼容旧格式 {"class": "person", "confidence": 0.8}
    person_count = sum(
        1 for d in detections
        if d.get("action") == "person" or d.get("class") == "person"
    )
    max_confidence = max(
        [d.get("confidence", 0) for d in detections], default=0
    )

    parts = [
        "RESULT",
        f"event={event_type}",
        f"task_id={task_id or '-'}",
        f"source_id={source_id or '-'}",
        f"frame={frame_count if frame_count is not None else '-'}",
        f"alert_count={alert_count if alert_count is not None else 0}",
        f"person_count={person_count}",
        f"max_confidence={max_confidence:.3f}"
    ]

    for key, value in extra.items():
        parts.append(f"{key}={value}")

    logger.warning(" | ".join(parts))


def generate_frames(source, source_id, is_file=False):
    """
    处理实时视频并生成MJPEG流
    主要用于摄像头/RTSP
    """
    global detector

    with process_lock:
        if source_id in active_processes:
            logger.warning(f"Source {source_id} already processing")
            return
        active_processes[source_id] = True
        logger.info(f"Start processing source: {source_id} (Type: {'File' if is_file else 'Stream'})")

    cap = None
    frame_count = 0
    alert_count = 0
    start_time = time.time()
    alert = None

    try:
        if is_file:
            cap = cv2.VideoCapture(source)
            logger.info(f"Opened video file: {source}")
        else:
            if isinstance(source, str) and source.isdigit():
                source = int(source)
            cap = cv2.VideoCapture(source)
            logger.info(f"Opened video stream: {source}")

        if not cap.isOpened():
            logger.error(f"Failed to open source: {source}")
            return

        while active_processes.get(source_id, False):
            success, frame = cap.read()
            if not success:
                if is_file:
                    logger.info(f"Video processing completed - Source: {source_id}, Total frames: {frame_count}")
                else:
                    logger.warning(f"Stream disconnected - Source: {source_id}")
                break

            frame_count += 1

            if frame_count % DETECTION_INTERVAL == 0:
                processed_frame, alert = analyze_frame(frame)
                annotated_frame = processed_frame.copy()

                logger.debug(f"[STREAM ALERT DEBUG] source={source_id}, frame={frame_count}, alert={alert}")

                if alert:
                    alert_count += 1
                    stream_alerts[source_id] = alert

                    cv2.rectangle(annotated_frame, (10, 10), (500, 80), (0, 0, 255), -1)
                    cv2.putText(
                        annotated_frame, alert, (20, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3
                    )
                    logger.warning(
                        f"ALERT - {alert} - Source: {source_id}, Frame: {frame_count}, Total alerts: {alert_count}"
                    )

                    log_result_event(
                        event_type="fight_detected",
                        source_id=source_id,
                        frame_count=frame_count,
                        alert_count=alert_count,
                        detections=[],
                        extra={"mode": "realtime"}
                    )
                else:
                    stream_alerts[source_id] = ""
            else:
                annotated_frame = frame.copy()
                if alert:
                    cv2.putText(
                        annotated_frame, alert, (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 4
                    )

            cv2.putText(
                annotated_frame, f"FPS: {FPS_LIMIT}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

            if frame_count % 100 == 0:
                elapsed_time = time.time() - start_time
                fps_actual = frame_count / elapsed_time if elapsed_time > 0 else 0
                logger.debug(
                    f"Progress - Source: {source_id}, Frames: {frame_count}, Actual FPS: {fps_actual:.2f}, Alerts: {alert_count}"
                )

            ok, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ok:
                continue

            frame_bytes = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )

            time.sleep(1 / FPS_LIMIT)

    except Exception as e:
        logger.error(f"Error processing source {source_id}: {str(e)}", exc_info=True)

    finally:
        if cap:
            cap.release()

        with process_lock:
            active_processes.pop(source_id, None)

        stream_alerts.pop(source_id, None)

        elapsed_time = time.time() - start_time
        logger.info(f"Stop processing source: {source_id}")
        logger.info(
            f"Statistics - Total frames: {frame_count}, Duration: {elapsed_time:.2f}s, "
            f"Avg FPS: {frame_count / elapsed_time if elapsed_time > 0 else 0:.2f}, Total alerts: {alert_count}"
        )

# ====================== 5. 长视频任务处理 ======================
def make_task_snapshot(task):
    """返回适合前端展示的任务信息"""
    return {
        "task_id": task["task_id"],
        "source_id": task["source_id"],
        "filename": task["filename"],
        "status": task["status"],
        "progress": task["progress"],
        "current_frame": task["current_frame"],
        "total_frames": task["total_frames"],
        "alert_count": task["alert_count"],
        "latest_alert": task.get("latest_alert", ""),
        "error": task["error"],
        "created_at": task["created_at"],
        "updated_at": task["updated_at"],
        "result_url": f"/result_video?task_id={task['task_id']}" if task["status"] == "completed" else None,
        "detected_type": task.get("detected_type", ""),
    }

def analyze_frame(frame):
    global detector

    if detector is None:
        raise RuntimeError("Detector not loaded")

    processed_frame, results = detector.process_frame(frame)

    alert = ""
    for item in results or []:
        action = item.get("action")
        if action and action != "Unknown":
            alert = normalize_alert_label(action)
            break

    return processed_frame, alert

def process_video_task(task_id):
    """后台处理上传视频任务，输出结果 MP4，并转码为浏览器兼容格式"""
    global detector

    cap = None
    writer = None
    start_time = time.time()
    raw_result_path = ""
    final_result_path = ""

    with tasks_lock:
        task = tasks.get(task_id)
        if not task:
            logger.error(f"Task not found when starting: {task_id}")
            return
        task["status"] = "processing"
        task["updated_at"] = time.time()
        task["latest_alert"] = ""

    try:
        file_path = task["file_path"]
        logger.info(f"Task start processing - Task: {task_id}, File: {file_path}")

        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            raise Exception("Failed to open uploaded video")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        src_fps = cap.get(cv2.CAP_PROP_FPS) or OUTPUT_FPS
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

        if width <= 0 or height <= 0:
            raise Exception("Invalid video resolution")

        raw_result_path = os.path.join("results", f"{task_id}_raw.mp4")
        final_result_path = os.path.join("results", f"{task_id}.mp4")

        for path in [raw_result_path, final_result_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning(f"Failed to remove old file: {path}, error: {str(e)}")

        fourcc = cv2.VideoWriter_fourcc(*OUTPUT_CODEC)
        writer = cv2.VideoWriter(
            raw_result_path,
            fourcc,
            OUTPUT_FPS or src_fps,
            (width, height)
        )

        if not writer.isOpened():
            raise Exception("Failed to open output video writer")

        with tasks_lock:
            if task_id not in tasks:
                raise Exception("Task removed unexpectedly")
            tasks[task_id]["total_frames"] = total_frames
            tasks[task_id]["result_path"] = ""
            tasks[task_id]["latest_alert"] = ""
            tasks[task_id]["detected_type"] = ""
            tasks[task_id]["updated_at"] = time.time()

        frame_count = 0
        alert_count = 0
        last_alert = ""

        while True:
            with tasks_lock:
                current_task = tasks.get(task_id)
                if not current_task:
                    raise Exception("Task not found during processing")
                if current_task["status"] == "stopped":
                    logger.info(f"Task stopped by user - Task: {task_id}")
                    break

            success, frame = cap.read()
            if not success:
                break

            frame_count += 1

            if frame_count % DETECTION_INTERVAL == 0:
                processed_frame, alert = analyze_frame(frame)
                annotated_frame = processed_frame.copy()
                last_alert = alert or ""

                if alert:
                    alert_count += 1

                    with tasks_lock:
                        if task_id in tasks:
                            tasks[task_id]["latest_alert"] = alert
                            tasks[task_id]["detected_type"] = alert

                    cv2.rectangle(annotated_frame, (10, 10), (500, 80), (0, 0, 255), -1)
                    cv2.putText(
                        annotated_frame, alert, (20, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3
                    )
                    logger.warning(
                        f"TASK ALERT - {alert} - Task: {task_id}, Frame: {frame_count}, Total alerts: {alert_count}"
                    )
                else:
                    with tasks_lock:
                        if task_id in tasks:
                            tasks[task_id]["latest_alert"] = ""
            else:
                annotated_frame = frame.copy()
                if last_alert:
                    cv2.putText(
                        annotated_frame, last_alert, (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 4
                    )

            cv2.putText(
                annotated_frame, f"TASK FPS: {OUTPUT_FPS}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

            writer.write(annotated_frame)

            progress = int(frame_count * 95 / total_frames) if total_frames > 0 else 0

            with tasks_lock:
                if task_id in tasks:
                    tasks[task_id]["current_frame"] = frame_count
                    tasks[task_id]["progress"] = progress
                    tasks[task_id]["alert_count"] = alert_count
                    tasks[task_id]["latest_alert"] = last_alert or ""
                    tasks[task_id]["updated_at"] = time.time()

            if frame_count % 100 == 0:
                elapsed_time = time.time() - start_time
                fps_actual = frame_count / elapsed_time if elapsed_time > 0 else 0
                logger.info(
                    f"Task progress - Task: {task_id}, Frames: {frame_count}/{total_frames}, "
                    f"Progress: {progress}%, Actual FPS: {fps_actual:.2f}, Alerts: {alert_count}"
                )

        with tasks_lock:
            current_task = tasks.get(task_id)
            if current_task and current_task["status"] == "stopped":
                logger.info(f"Task processing stopped before transcode - Task: {task_id}")
                return

        if writer:
            writer.release()
            writer = None

        if not os.path.exists(raw_result_path) or os.path.getsize(raw_result_path) <= 1024:
            raise Exception("raw result video file invalid or empty")

        raw_size_mb = os.path.getsize(raw_result_path) / (1024 * 1024)
        logger.info(f"Raw result video saved - Task: {task_id}, Path: {raw_result_path}, Size: {raw_size_mb:.2f}MB")

        with tasks_lock:
            if task_id in tasks:
                tasks[task_id]["status"] = "transcoding"
                tasks[task_id]["progress"] = 97
                tasks[task_id]["updated_at"] = time.time()

        transcode_to_browser_mp4(raw_result_path, final_result_path)

        if not os.path.exists(final_result_path) or os.path.getsize(final_result_path) <= 1024:
            raise Exception("final browser mp4 not generated")

        final_size_mb = os.path.getsize(final_result_path) / (1024 * 1024)
        logger.info(f"Final browser video saved - Task: {task_id}, Path: {final_result_path}, Size: {final_size_mb:.2f}MB")

        with tasks_lock:
            if task_id in tasks:
                if tasks[task_id]["status"] != "stopped":
                    tasks[task_id]["result_path"] = final_result_path
                    tasks[task_id]["status"] = "completed"
                    tasks[task_id]["progress"] = 100
                tasks[task_id]["updated_at"] = time.time()

        elapsed = time.time() - start_time
        logger.info(
            f"Task completed - Task: {task_id}, Frames: {frame_count}, Alerts: {alert_count}, Duration: {elapsed:.2f}s"
        )

        try:
            if os.path.exists(raw_result_path):
                os.remove(raw_result_path)
                logger.info(f"Removed raw result file: {raw_result_path}")
        except Exception as e:
            logger.warning(f"Failed to remove raw result file: {str(e)}")

    except Exception as e:
        logger.error(f"Task failed - Task: {task_id}, Error: {str(e)}", exc_info=True)
        with tasks_lock:
            if task_id in tasks:
                tasks[task_id]["status"] = "failed"
                tasks[task_id]["error"] = str(e)
                tasks[task_id]["updated_at"] = time.time()

    finally:
        if cap:
            cap.release()
        if writer:
            writer.release()

# ====================== 6. API接口 ======================
@app.route('/')
def home():
    logger.info(f"API access - Path: /, IP: {request.remote_addr}")
    return jsonify({
        "name": "Campus Security System",
        "version": "2.1-task-mode-browser-video",
        "status": "running",
        "model_loaded": detector is not None,
        "endpoints": {
            "GET /": "API information",
            "GET /status": "System status",
            "GET /logs": "View logs",
            "GET /video_feed": "Realtime video stream (camera/RTSP)",
            "POST /upload_video": "Upload video and create task",
            "GET /task_status?task_id=...": "Check task status",
            "GET /tasks": "List tasks",
            "GET /result_video?task_id=...": "Get processed result video",
            "GET /stop?source_id=...": "Stop realtime stream",
            "GET /stop_task?task_id=...": "Stop upload task",
            "GET /stop_all": "Stop all realtime streams",
            "GET /stream_status?source_id=...": "Get latest alert of realtime stream",
        }
    })

@app.route('/status')
def status():
    logger.debug(f"Status check - IP: {request.remote_addr}")
    with tasks_lock:
        task_count = len(tasks)
        processing_tasks = [
            t["task_id"] for t in tasks.values()
            if t["status"] in ["processing", "transcoding"]
        ]

    return jsonify({
        "status": "ok",
        "model_loaded": detector is not None,
        "active_streams": len(active_processes),
        "active_list": list(active_processes.keys()),
        "task_count": task_count,
        "processing_tasks": processing_tasks
    })


def parse_log_line(line, index):
    text = str(line).strip()

    pattern = r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[([A-Z]+)\](?:\s+\[([^\]]+)\])?\s*(.*)$'
    match = re.match(pattern, text)

    if match:
        return {
            "index": index + 1,
            "raw": text,
            "time": match.group(1),
            "level": match.group(2),
            "source": match.group(3) if match.group(3) else "-",
            "message": match.group(4) if match.group(4) else "-"
        }

    return {
        "index": index + 1,
        "raw": text,
        "time": "-",
        "level": "-",
        "source": "-",
        "message": text or "-"
    }


@app.route('/logs')
def get_logs():
    log_type = request.args.get('type', 'app')

    try:
        lines = max(1, int(request.args.get('lines', 50)))
    except ValueError:
        lines = 50

    log_files = {
        'app': 'logs/campus_security.log',
        'error': 'logs/error.log',
        'alert': 'logs/alert.log'
    }

    log_file = log_files.get(log_type, 'logs/campus_security.log')

    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

                parsed_items = [
                    parse_log_line(line, idx)
                    for idx, line in enumerate(recent_lines)
                ]
                print("GET_LOGS_NEW_VERSION_TRIGGERED")
                print("parsed_items sample =", parsed_items[:1])
                return jsonify({
                    "type": log_type,
                    "lines": recent_lines,
                    "items": parsed_items,
                    "total_lines": len(all_lines)
                })
        else:
            return jsonify({"error": "Log file not found"}), 404
    except Exception as e:
        logger.error(f"Failed to read log file: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/video_feed')
def video_feed():
    """
    实时视频流接口
    - 本地摄像头：/video_feed?source=0
    - RTSP监控：/video_feed?source=rtsp://...
    """
    source = request.args.get('source', '0')
    source_id = f"stream_{source}"

    logger.info(f"Video feed request - Source: {source}, IP: {request.remote_addr}")

    if source_id in active_processes:
        logger.info(f"Stopping existing stream: {source_id}")
        active_processes[source_id] = False
        time.sleep(0.5)

    return Response(
        generate_frames(source, source_id, is_file=False),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/stream_status')
def stream_status():
    source_id = request.args.get('source_id')
    if not source_id:
        return jsonify({"error": "source_id parameter required"}), 400

    return jsonify({
        "source_id": source_id,
        "latest_alert": stream_alerts.get(source_id, "")
    })

@app.route('/upload_video', methods=['POST'])
def upload_video():
    """
    上传视频文件接口
    前端用 FormData 上传，字段名: video
    返回 JSON，不再直接回 MJPEG 流
    """
    if 'video' not in request.files:
        logger.warning(f"Upload request missing file - IP: {request.remote_addr}")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['video']
    if file.filename == '':
        logger.warning(f"Upload filename empty - IP: {request.remote_addr}")
        return jsonify({"error": "Empty filename"}), 400

    original_name = file.filename
    safe_name = secure_filename(original_name)
    if not safe_name:
        safe_name = f"video_{int(time.time())}.mp4"

    timestamp = int(time.time())
    filename = f"{timestamp}_{safe_name}"
    temp_path = os.path.join("temp", filename)
    file.save(temp_path)

    file_size = os.path.getsize(temp_path) / (1024 * 1024)
    source_id = f"file_{filename}"
    task_id = f"task_{timestamp}_{int(time.time() * 1000) % 100000}"

    logger.info(
        f"Video file received - Filename: {original_name}, Saved: {filename}, Size: {file_size:.2f}MB, IP: {request.remote_addr}"
    )

    task = {
        "task_id": task_id,
        "source_id": source_id,
        "filename": original_name,
        "safe_filename": filename,
        "file_path": temp_path,
        "result_path": "",
        "status": "queued",
        "progress": 0,
        "current_frame": 0,
        "total_frames": 0,
        "alert_count": 0,
        "latest_alert": "",
        "error": "",
        "created_at": time.time(),
        "updated_at": time.time(),
        "detected_type": "",
    }

    with tasks_lock:
        tasks[task_id] = task

    thread = threading.Thread(target=process_video_task, args=(task_id,), daemon=True)
    thread.start()

    return jsonify({
        "message": "upload success",
        "task_id": task_id,
        "source_id": source_id,
        "filename": original_name,
        "status": "queued"
    })


@app.route('/task_status')
def task_status():
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "task_id parameter required"}), 400

    with tasks_lock:
        task = tasks.get(task_id)

    if not task:
        return jsonify({"error": "task not found"}), 404

    return jsonify(make_task_snapshot(task))


@app.route('/tasks')
def list_tasks():
    with tasks_lock:
        task_list = [make_task_snapshot(task) for task in tasks.values()]

    task_list.sort(key=lambda x: x["created_at"], reverse=True)
    return jsonify({
        "count": len(task_list),
        "tasks": task_list
    })


@app.route('/result_video')
def result_video():
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "task_id parameter required"}), 400

    with tasks_lock:
        task = tasks.get(task_id)

    if not task:
        return jsonify({"error": "task not found"}), 404

    if task["status"] != "completed":
        return jsonify({"error": f"task not completed, current status: {task['status']}"}), 400

    result_path = task["result_path"]
    if not result_path or not os.path.exists(result_path):
        return jsonify({"error": "result file not found"}), 404

    return send_file(result_path, mimetype='video/mp4', as_attachment=False)


@app.route('/stop')
def stop():
    """停止指定实时源检测"""
    source_id = request.args.get('source_id')

    if not source_id:
        logger.warning(f"Stop request missing source_id - IP: {request.remote_addr}")
        return jsonify({"error": "source_id parameter required"}), 400

    logger.info(f"Stop request - Source: {source_id}, IP: {request.remote_addr}")

    if source_id in active_processes:
        active_processes[source_id] = False
        return jsonify({"message": f"Stopped: {source_id}"})
    else:
        logger.warning(f"Attempt to stop non-existent source: {source_id}")
        return jsonify({"message": f"Source not found: {source_id}"}), 404


@app.route('/stop_task')
def stop_task():
    """停止长视频任务"""
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "task_id parameter required"}), 400

    with tasks_lock:
        task = tasks.get(task_id)
        if not task:
            return jsonify({"error": "task not found"}), 404

        if task["status"] in ["completed", "failed", "stopped"]:
            return jsonify({"message": f"Task already {task['status']}", "task_id": task_id})

        task["status"] = "stopped"
        task["updated_at"] = time.time()

    logger.info(f"Task stop requested - Task: {task_id}, IP: {request.remote_addr}")
    return jsonify({"message": "task stop requested", "task_id": task_id})


@app.route('/stop_all')
def stop_all():
    """停止所有实时流"""
    count = len(active_processes)
    logger.info(f"Stop all request - Active sources: {count}, IP: {request.remote_addr}")

    for source_id in list(active_processes.keys()):
        active_processes[source_id] = False

    return jsonify({"message": f"Stopped {count} realtime detection processes"})


# ====================== 7. 启动服务 ======================
if __name__ == '__main__':
    print("=" * 50)
    print("Campus Security System v2.1-task-mode-browser-video")
    print("=" * 50)

    logger.info("=" * 50)
    logger.info("Campus Security System starting")
    logger.info("=" * 50)

    if load_model():
        print("\n" + "=" * 50)
        print("System started successfully")
        print("=" * 50)
        print(f"Local access: http://127.0.0.1:{PORT}")
        print(f"External access: http://your-ip:{PORT}")
        print(f"\nTest endpoints:")
        print(f"  http://127.0.0.1:{PORT}/status")
        print(f"  http://127.0.0.1:{PORT}/tasks")
        print(f"  http://127.0.0.1:{PORT}/logs")
        print(f"\nRealtime stream:")
        print(f"  http://127.0.0.1:{PORT}/video_feed?source=0")
        print("\nPress Ctrl+C to stop")
        print("=" * 50)

        logger.info(f"Server started - Host: {HOST}, Port: {PORT}")

        try:
            app.run(host=HOST, port=PORT, debug=False, threaded=True)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
    else:
        print("\n" + "=" * 50)
        print("System failed to start")
        print("=" * 50)
        print("Please ensure POSE and LSTM model files exist (check POSE_MODEL_PATH and LSTM_MODEL_PATH in config.py)")
        logger.error("System failed to start - model not found")