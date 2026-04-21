# config.py
import os

# ====================== 配置区 ======================
# 模型路径（模型负责人把 best.pt 放这里）
MODEL_PATH = "models/best.pt"

# 检测参数
CONF_THRESHOLD = 0.45      # 置信度阈值
IOU_THRESHOLD = 0.45       # IOU阈值

# 服务器配置
HOST = '0.0.0.0'           # 允许外部访问
PORT = 5000                # 端口号

# 视频处理参数
FPS_LIMIT = 30             # 限制帧率
DETECTION_INTERVAL = 5     # 每5帧检测一次

# ====================== 自动创建文件夹 ======================
os.makedirs("models", exist_ok=True)
os.makedirs("temp", exist_ok=True)