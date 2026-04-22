import os

# ====================== 模型配置 ======================
POSE_MODEL_PATH = "models/yolov8n-pose.pt"
LSTM_MODEL_PATH = "models/best_model.pth"

# ====================== 检测参数 ======================
CONF_THRESHOLD = 0.45
IOU_THRESHOLD = 0.45
DETECTION_INTERVAL = 5

# ====================== 视频处理参数 ======================
FPS_LIMIT = 20           # 使用新版 FPS
OUTPUT_FPS = 20
OUTPUT_CODEC = 'mp4v'   # OpenCV 编码，最终可用 ffmpeg 转码

# ====================== 上传限制（MB） ======================
MAX_CONTENT_LENGTH_MB = 2048

# ====================== 服务器配置 ======================
HOST = '0.0.0.0'
PORT = 5000

# ====================== 自动创建文件夹 ======================
os.makedirs("models", exist_ok=True)
os.makedirs("temp", exist_ok=True)
os.makedirs("results", exist_ok=True)
os.makedirs("logs", exist_ok=True)