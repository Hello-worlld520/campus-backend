import os

# ====================== 配置区 ======================
MODEL_PATH = "models/best.pt"

# 检测参数
CONF_THRESHOLD = 0.45
IOU_THRESHOLD = 0.45

# 服务器配置
HOST = '0.0.0.0'
PORT = 5000

# 视频处理参数
FPS_LIMIT = 30
DETECTION_INTERVAL = 5

# 结果视频参数
OUTPUT_FPS = 20
OUTPUT_CODEC = 'mp4v'   # 这里仍然作为 raw 文件的 OpenCV 编码，最终会被 ffmpeg 转码

# 上传限制（MB）
MAX_CONTENT_LENGTH_MB = 2048

# ====================== 自动创建文件夹 ======================
os.makedirs("models", exist_ok=True)
os.makedirs("temp", exist_ok=True)
os.makedirs("results", exist_ok=True)
os.makedirs("logs", exist_ok=True)