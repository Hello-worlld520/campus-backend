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
from ultralytics import YOLO
from config import *

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
    
    print("\n 检查模型文件...")
    
    if not os.path.exists(MODEL_PATH):
        print(f" 错误：找不到模型文件")
        print(f"   期望路径：{MODEL_PATH}")
        print(f"\n 解决方案：")
        print(f"   1. 把训练好的 best.pt 放到 models/ 文件夹")
        print(f"   2. 或者修改 config.py 中的 MODEL_PATH")
        return False
    
    try:
        print(f" 正在加载模型：{MODEL_PATH}")
        model = YOLO(MODEL_PATH)
        print(f" 模型加载成功！")
        return True
    except Exception as e:
        print(f" 模型加载失败：{str(e)}")
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
                    alert = "检测到打架行为！"
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
            print(f" 源 {source_id} 已在处理中")
            return
        active_processes[source_id] = True
    
    cap = None
    frame_count = 0
    
    try:
        # 打开视频源
        if is_file:
            cap = cv2.VideoCapture(source)
            print(f" 开始处理视频文件：{source}")
        else:
            # 处理摄像头或RTSP流
            if isinstance(source, str) and source.isdigit():
                source = int(source)
            cap = cv2.VideoCapture(source)
            print(f" 开始处理视频流：{source}")
        
        if not cap.isOpened():
            print(f" 无法打开视频源：{source}")
            return
        
        # 主循环
        while active_processes.get(source_id, False):
            success, frame = cap.read()
            if not success:
                if is_file:
                    print(f" 视频处理完成")
                else:
                    print(f" 视频流断开")
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
                    # 红色背景框
                    cv2.rectangle(annotated_frame, (10, 10), (500, 80), (0, 0, 255), -1)
                    cv2.putText(annotated_frame, alert, (20, 55),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
                    print(f"🚨 {alert} (源: {source_id})")
            else:
                # 不检测，只显示原帧
                annotated_frame = frame.copy()
                if 'alert' in locals() and alert:
                    cv2.putText(annotated_frame, alert, (30, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 4)
            
            # 添加FPS显示
            cv2.putText(annotated_frame, f"FPS: {FPS_LIMIT}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 编码为JPEG
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            
            # 生成MJPEG流
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # 控制帧率
            time.sleep(1 / FPS_LIMIT)
            
    except Exception as e:
        print(f" 处理出错：{str(e)}")
    
    finally:
        # 清理资源
        if cap:
            cap.release()
        with process_lock:
            active_processes.pop(source_id, None)
        print(f"📹 停止处理：{source_id}")

# ====================== 4. API接口 ======================

@app.route('/')
def home():
    """首页 - API信息"""
    return jsonify({
        "name": "校园安防后端",
        "version": "1.0",
        "status": "running",
        "model_loaded": model is not None,
        "endpoints": {
            "GET /": "API信息",
            "GET /status": "系统状态",
            "GET /video_feed": "视频流 (参数: source=0 或 source=rtsp://...)",
            "POST /upload_video": "上传视频文件",
            "GET /stop": "停止检测"
        }
    })

@app.route('/status')
def status():
    """系统状态接口"""
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "active_streams": len(active_processes),
        "active_list": list(active_processes.keys())
    })

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
    
    # 如果已经在处理，先停止
    if source_id in active_processes:
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
        return jsonify({"error": "没有上传文件"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400
    
    # 保存文件
    timestamp = int(time.time())
    filename = f"{timestamp}_{file.filename}"
    temp_path = os.path.join("temp", filename)
    file.save(temp_path)
    
    source_id = f"file_{filename}"
    
    print(f" 收到视频：{file.filename}")
    
    return Response(
        generate_frames(temp_path, source_id, is_file=True),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/stop')
def stop():
    """停止指定源的检测"""
    source_id = request.args.get('source_id')
    
    if not source_id:
        return jsonify({"error": "请指定 source_id 参数"}), 400
    
    if source_id in active_processes:
        active_processes[source_id] = False
        return jsonify({"message": f"已停止：{source_id}"})
    else:
        return jsonify({"message": f"未找到：{source_id}"}), 404

@app.route('/stop_all')
def stop_all():
    """停止所有检测"""
    for source_id in list(active_processes.keys()):
        active_processes[source_id] = False
    return jsonify({"message": f"已停止 {len(active_processes)} 个检测"})

# ====================== 5. 启动服务 ======================
if __name__ == '__main__':
    print("=" * 50)
    print("🎬 校园安防后端系统 v1.0")
    print("=" * 50)
    
    if load_model():
        print("\n" + "=" * 50)
        print(" 启动成功！")
        print("=" * 50)
        print(f"📍 本地访问：http://127.0.0.1:{PORT}")
        print(f"📍 外部访问：http://你的IP:{PORT}")
        print(f"\n📡 测试接口：")
        print(f"   http://127.0.0.1:{PORT}/status")
        print(f"\n🎥 视频流测试：")
        print(f"   http://127.0.0.1:{PORT}/video_feed?source=0")
        print("\n  按 Ctrl+C 停止服务")
        print("=" * 50)
        
        app.run(host=HOST, port=PORT, debug=False, threaded=True)
    else:
        print("\n 启动失败！")
        print("请确保 models/best.pt 文件存在")