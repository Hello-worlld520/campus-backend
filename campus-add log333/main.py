# -*- coding: utf-8 -*-
"""
校园安防后端 - 版本一（极简版）
"""

from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import cv2
import os
import time
import threading
import logging
from logging.handlers import RotatingFileHandler
from ultralytics import YOLO
from config import *

# ====================== 日志配置 ======================
def setup_logger():
    """配置日志系统"""
    # 创建logs目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 创建logger
    logger = logging.getLogger('CampusSecurity')
    logger.setLevel(logging.DEBUG)
    
    # 防止重复添加handler
    if logger.handlers:
        return logger
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 详细格式用于文件日志
    detailed_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 文件handler - 所有日志
    file_handler = RotatingFileHandler(
        'logs/campus_security.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # 错误日志单独文件
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # 告警日志单独文件
    alert_handler = RotatingFileHandler(
        'logs/alert.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    alert_handler.setLevel(logging.WARNING)
    alert_handler.setFormatter(detailed_formatter)
    
    # 添加handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(alert_handler)
    
    return logger

# 初始化日志
logger = setup_logger()

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

# 全局变量
model = None
active_processes = {}  # 记录正在处理的视频源
process_lock = threading.Lock()

# ====================== 1. 加载模型 ======================
def load_model():
    """加载YOLO模型"""
    global model
    
    logger.info("=" * 50)
    logger.info("Checking model files...")
    
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Model file not found at: {MODEL_PATH}")
        logger.info("Solutions:")
        logger.info("  1. Place best.pt in models/ folder")
        logger.info("  2. Update MODEL_PATH in config.py")
        return False
    
    try:
        logger.info(f"Loading model: {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
        logger.info("Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}", exc_info=True)
        return False

# ====================== 2. 行为分析函数 ======================
def analyze_behavior(results):
    """
    分析检测结果，判断是否有打架行为
    """
    detections = []
    alert = None
    
    # 收集所有人形检测
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
            class_name = model.names[cls_id]
            
            detections.append({
                "class": class_name,
                "confidence": round(conf, 3),
                "bbox": [x1, y1, x2, y2]
            })
            
            # 如果是人，记录位置
            if class_name == "person":
                persons.append({
                    "center": ((x1 + x2) // 2, (y1 + y2) // 2),
                    "bbox": [x1, y1, x2, y2]
                })
    
    # 打架检测：两个人距离太近
    if len(persons) >= 2:
        for i in range(len(persons)):
            for j in range(i + 1, len(persons)):
                # 计算距离
                dx = persons[i]["center"][0] - persons[j]["center"][0]
                dy = persons[i]["center"][1] - persons[j]["center"][1]
                distance = (dx**2 + dy**2) ** 0.5
                
                # 距离小于150像素认为是打架
                if distance < 150:
                    alert = "Fight detected!"
                    logger.warning(f"Fight detected - distance: {distance:.2f}px")
                    break
            if alert:
                break
    
    return detections, alert

# ====================== 3. 视频流生成器 ======================
def generate_frames(source, source_id, is_file=False):
    """
    处理视频并生成MJPEG流
    """
    global model
    
    # 标记这个源正在处理
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
    
    try:
        # 打开视频源
        if is_file:
            cap = cv2.VideoCapture(source)
            logger.info(f"Opened video file: {source}")
        else:
            # 处理摄像头或RTSP流
            if isinstance(source, str) and source.isdigit():
                source = int(source)
            cap = cv2.VideoCapture(source)
            logger.info(f"Opened video stream: {source}")
        
        if not cap.isOpened():
            logger.error(f"Failed to open source: {source}")
            return
        
        # 获取视频信息
        if is_file:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"Video info - Total frames: {total_frames}, FPS: {fps}")
        
        # 主循环
        while active_processes.get(source_id, False):
            success, frame = cap.read()
            if not success:
                if is_file:
                    logger.info(f"Video processing completed - Source: {source_id}, Total frames: {frame_count}")
                else:
                    logger.warning(f"Stream disconnected - Source: {source_id}")
                break
            
            frame_count += 1
            
            # 每隔几帧检测一次（性能优化）
            if frame_count % DETECTION_INTERVAL == 0:
                # YOLO检测
                results = model(frame, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD, verbose=False)
                
                # 行为分析
                detections, alert = analyze_behavior(results)
                
                # 绘制检测结果
                annotated_frame = results[0].plot()
                
                # 添加警报文字
                if alert:
                    alert_count += 1
                    # 红色背景框
                    cv2.rectangle(annotated_frame, (10, 10), (500, 80), (0, 0, 255), -1)
                    cv2.putText(annotated_frame, alert, (20, 55),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
                    logger.warning(f"ALERT - {alert} - Source: {source_id}, Frame: {frame_count}, Total alerts: {alert_count}")
            else:
                # 不检测，只显示原帧
                annotated_frame = frame.copy()
                if 'alert' in locals() and alert:
                    cv2.putText(annotated_frame, alert, (30, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 4)
            
            # 添加FPS显示
            cv2.putText(annotated_frame, f"FPS: {FPS_LIMIT}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 每100帧记录一次进度
            if frame_count % 100 == 0:
                elapsed_time = time.time() - start_time
                fps_actual = frame_count / elapsed_time if elapsed_time > 0 else 0
                logger.debug(f"Progress - Source: {source_id}, Frames: {frame_count}, Actual FPS: {fps_actual:.2f}, Alerts: {alert_count}")
            
            # 编码为JPEG
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            
            # 生成MJPEG流
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # 控制帧率
            time.sleep(1 / FPS_LIMIT)
            
    except Exception as e:
        logger.error(f"Error processing source {source_id}: {str(e)}", exc_info=True)
    
    finally:
        # 清理资源
        if cap:
            cap.release()
        with process_lock:
            active_processes.pop(source_id, None)
        
        # 记录处理统计
        elapsed_time = time.time() - start_time
        logger.info(f"Stop processing source: {source_id}")
        logger.info(f"Statistics - Total frames: {frame_count}, Duration: {elapsed_time:.2f}s, "
                   f"Avg FPS: {frame_count/elapsed_time if elapsed_time > 0 else 0:.2f}, Total alerts: {alert_count}")

# ====================== 4. API接口 ======================

@app.route('/')
def home():
    """首页 - API信息"""
    logger.info(f"API access - Path: /, IP: {request.remote_addr}")
    return jsonify({
        "name": "Campus Security System",
        "version": "1.0",
        "status": "running",
        "model_loaded": model is not None,
        "endpoints": {
            "GET /": "API information",
            "GET /status": "System status",
            "GET /logs": "View logs",
            "GET /video_feed": "Video stream (params: source=0 or source=rtsp://...)",
            "POST /upload_video": "Upload video file",
            "GET /stop": "Stop detection"
        }
    })

@app.route('/status')
def status():
    """系统状态接口"""
    logger.debug(f"Status check - IP: {request.remote_addr}")
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "active_streams": len(active_processes),
        "active_list": list(active_processes.keys())
    })

@app.route('/logs')
def get_logs():
    """查看最近的日志"""
    log_type = request.args.get('type', 'app')
    lines = int(request.args.get('lines', 50))
    
    log_files = {
        'app': 'logs/campus_security.log',
        'error': 'logs/error.log',
        'alert': 'logs/alert.log'
    }
    
    log_file = log_files.get(log_type, 'logs/campus_security.log')
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                # 读取最后N行
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return jsonify({
                    "type": log_type,
                    "lines": recent_lines,
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
    视频流接口
    使用方式：
    - 本地摄像头：/video_feed?source=0
    - RTSP监控：/video_feed?source=rtsp://admin:123456@192.168.1.100:554/stream1
    """
    source = request.args.get('source', '0')
    source_id = f"stream_{source}"
    
    logger.info(f"Video feed request - Source: {source}, IP: {request.remote_addr}")
    
    # 如果已经在处理，先停止
    if source_id in active_processes:
        logger.info(f"Stopping existing stream: {source_id}")
        active_processes[source_id] = False
        time.sleep(0.5)
    
    return Response(
        generate_frames(source, source_id, is_file=False),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/upload_video', methods=['POST'])
def upload_video():
    """
    上传视频文件接口
    前端用 FormData 上传，字段名: video
    """
    if 'video' not in request.files:
        logger.warning(f"Upload request missing file - IP: {request.remote_addr}")
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['video']
    if file.filename == '':
        logger.warning(f"Upload filename empty - IP: {request.remote_addr}")
        return jsonify({"error": "Empty filename"}), 400
    
    # 创建temp目录
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    # 保存文件
    timestamp = int(time.time())
    filename = f"{timestamp}_{file.filename}"
    temp_path = os.path.join("temp", filename)
    file.save(temp_path)
    
    source_id = f"file_{filename}"
    
    file_size = os.path.getsize(temp_path) / (1024 * 1024)  # MB
    logger.info(f"Video file received - Filename: {file.filename}, Size: {file_size:.2f}MB, IP: {request.remote_addr}")
    
    return Response(
        generate_frames(temp_path, source_id, is_file=True),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/stop')
def stop():
    """停止指定源的检测"""
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

@app.route('/stop_all')
def stop_all():
    """停止所有检测"""
    count = len(active_processes)
    logger.info(f"Stop all request - Active sources: {count}, IP: {request.remote_addr}")
    
    for source_id in list(active_processes.keys()):
        active_processes[source_id] = False
    
    return jsonify({"message": f"Stopped {count} detection processes"})

# ====================== 5. 启动服务 ======================
if __name__ == '__main__':
    print("=" * 50)
    print("Campus Security System v1.0")
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
        print(f"  http://127.0.0.1:{PORT}/logs")
        print(f"\nTest video stream:")
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
        print("Please ensure models/best.pt exists")
        logger.error("System failed to start - model not found")