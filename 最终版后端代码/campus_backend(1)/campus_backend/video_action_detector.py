"""
视频行为识别演示程序 - 混合模型版（LSTM + Self-Attention）
使用 YOLOv8n-pose + 混合模型 + 几何规则辅助
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import cv2
import numpy as np
from ultralytics import YOLO
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import deque, Counter
import time
import math

# ========== 动作映射 ==========
ACTION_ID_TO_NAME = {
    0: 'Kick', 1: 'Laying', 2: 'Phone', 3: 'Pointing', 4: 'Slap face',
    5: 'Slap table', 6: 'Smoking', 7: 'Squating', 8: 'Stand', 9: 'Touch', 10: 'Hit wall',
}
ACTION_NAME_TO_ID = {v: k for k, v in ACTION_ID_TO_NAME.items()}

# ========== 混合模型定义 ==========
class MultiHeadSelfAttention(nn.Module):
    def __init__(self, embed_dim, num_heads=4, dropout=0.1):
        super().__init__()
        assert embed_dim % num_heads == 0
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5
        self.qkv = nn.Linear(embed_dim, embed_dim * 3)
        self.attn_drop = nn.Dropout(dropout)
        self.proj = nn.Linear(embed_dim, embed_dim)
        self.proj_drop = nn.Dropout(dropout)

    def forward(self, x):
        B, N, C = x.shape
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)
        x = (attn @ v).transpose(1, 2).reshape(B, N, C)
        x = self.proj(x)
        x = self.proj_drop(x)
        return x

class PoseLSTMWithAttentionClassifier(nn.Module):
    def __init__(self, input_dim=34, hidden_dim=128, num_layers=2, num_heads=4, num_classes=11, dropout=0.2):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv1d(input_dim, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        self.attention = MultiHeadSelfAttention(embed_dim=hidden_dim*2, num_heads=num_heads, dropout=dropout)
        self.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim*2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        x = x.permute(0, 2, 1)          # (batch, 34, seq_len)
        x = self.cnn(x)                  # (batch, 128, seq_len)
        x = x.permute(0, 2, 1)          # (batch, seq_len, 128)
        lstm_out, _ = self.lstm(x)       # (batch, seq_len, hidden_dim*2)
        attn_out = self.attention(lstm_out)  # (batch, seq_len, hidden_dim*2)
        pooled = attn_out.mean(dim=1)    # (batch, hidden_dim*2)
        return self.fc(pooled)

# ========== 卡尔曼滤波器 ==========
class KalmanFilter1D:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-2, initial_value=0.0):
        self.q = process_noise
        self.r = measurement_noise
        self.x = initial_value
        self.p = 1.0
        self.k = 0.0

    def update(self, measurement):
        self.p = self.p + self.q
        self.k = self.p / (self.p + self.r)
        self.x = self.x + self.k * (measurement - self.x)
        self.p = (1 - self.k) * self.p
        return self.x

# ========== 主检测器 ==========
class VideoActionDetector:
    def __init__(self, model_path, pose_model_path='yolov8n-pose.pt'):
        print("加载YOLOv8-pose模型...")
        self.yolo_model = YOLO(pose_model_path)
        print("✓ YOLOv8官方模型加载成功")

        print(f"加载混合模型: {model_path}")
        self.lstm_model = PoseLSTMWithAttentionClassifier(
            input_dim=34,
            hidden_dim=128,
            num_layers=2,
            num_heads=4,
            num_classes=11,
            dropout=0.2
        )
        if os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location='cpu')
            self.lstm_model.load_state_dict(state_dict)
            print(f"✓ 混合模型加载成功")
        else:
            print(f"找不到混合模型: {model_path}")
            self.lstm_model = None
        if self.lstm_model is not None:
            self.lstm_model.eval()

        # 配置参数（注意 buffer_size 必须与训练时的 seq_len 一致，即 10）
        self.buffer_size = 10
        self.keypoints_buffer = {}
        self.frame_interval = 2
        self.frame_count = 0
        self.last_detection_frame = None
        self.last_detection_results = []
        self.action_smooth = {}
        self.smooth_window = 10
        self.kalman_filters = {}

        # 动作颜色映射
        self.action_colors = {
            'Kick': (0, 0, 255), 'Laying': (255, 0, 255), 'Phone': (255, 165, 0),
            'Pointing': (255, 255, 0), 'Slap face': (0, 0, 255), 'Slap table': (0, 165, 255),
            'Smoking': (128, 0, 128), 'Squating': (0, 255, 255), 'Stand': (0, 255, 0),
            'Touch': (255, 0, 0), 'Hit wall': (0, 0, 255), 'Unknown': (128, 128, 128)
        }

        # 关键点索引
        self.IDX = {
            'nose': 0, 'left_eye': 1, 'right_eye': 2, 'left_ear': 3, 'right_ear': 4,
            'left_shoulder': 5, 'right_shoulder': 6, 'left_elbow': 7, 'right_elbow': 8,
            'left_wrist': 9, 'right_wrist': 10, 'left_hip': 11, 'right_hip': 12,
            'left_knee': 13, 'right_knee': 14, 'left_ankle': 15, 'right_ankle': 16
        }

        # 骨架连线
        self.skeleton_edges = [
            (0,1),(0,2),(1,3),(2,4), (5,7),(7,9),(6,8),(8,10),
            (5,6),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)
        ]

    # ---------- 几何辅助函数 ----------
    def calculate_angle(self, p1, p2, p3):
        if p1 is None or p2 is None or p3 is None:
            return 0
        a = np.array(p1); b = np.array(p2); c = np.array(p3)
        ba = a - b; bc = c - b
        cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        return np.degrees(angle)

    def distance(self, p1, p2):
        if p1 is None or p2 is None:
            return 1.0
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def classify_by_geometry(self, kp_array):
        def get_kpt(idx):
            if idx < 17:
                return (kp_array[idx, 0], kp_array[idx, 1])
            return None
        nose = get_kpt(self.IDX['nose'])
        l_shoulder = get_kpt(self.IDX['left_shoulder'])
        r_shoulder = get_kpt(self.IDX['right_shoulder'])
        l_elbow = get_kpt(self.IDX['left_elbow'])
        r_elbow = get_kpt(self.IDX['right_elbow'])
        l_wrist = get_kpt(self.IDX['left_wrist'])
        r_wrist = get_kpt(self.IDX['right_wrist'])
        l_hip = get_kpt(self.IDX['left_hip'])
        r_hip = get_kpt(self.IDX['right_hip'])
        l_knee = get_kpt(self.IDX['left_knee'])
        r_knee = get_kpt(self.IDX['right_knee'])
        l_ankle = get_kpt(self.IDX['left_ankle'])
        r_ankle = get_kpt(self.IDX['right_ankle'])

        # 躺
        if l_shoulder and r_shoulder and l_hip and r_hip:
            body_width = abs(r_shoulder[0] - l_shoulder[0])
            body_height = abs((l_hip[1]+r_hip[1])/2 - (l_shoulder[1]+r_shoulder[1])/2)
            is_horizontal = body_height < 0.15
            if (body_height > 0 and body_width / body_height > 1.0) or is_horizontal:
                return 'Laying', 0.85

        # 站立/蹲下
        if l_hip and r_hip and l_knee and r_knee:
            hip_y = (l_hip[1] + r_hip[1]) / 2
            knee_y = (l_knee[1] + r_knee[1]) / 2
            if abs(hip_y - knee_y) < 0.15:
                return 'Squating', 0.85
            if hip_y < knee_y - 0.25:
                if l_shoulder and r_shoulder:
                    body_h = abs((l_hip[1]+r_hip[1])/2 - (l_shoulder[1]+r_shoulder[1])/2)
                    body_w = abs(r_shoulder[0] - l_shoulder[0])
                    if body_w > 0 and body_h / body_w > 1.0 and body_h > 0.15:
                        return 'Stand', 0.8

        # 踢腿
        if l_ankle and l_knee and l_ankle[1] < l_knee[1]:
            return 'Kick', 0.8
        if r_ankle and r_knee and r_ankle[1] < r_knee[1]:
            return 'Kick', 0.8

        # 打电话
        if nose and l_wrist and self.distance(l_wrist, nose) < 0.15:
            return 'Phone', 0.8
        if nose and r_wrist and self.distance(r_wrist, nose) < 0.15:
            return 'Phone', 0.8

        # 指
        if l_shoulder and l_elbow and l_wrist:
            angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
            if angle > 150 and l_wrist[1] < l_shoulder[1]:
                return 'Pointing', 0.75
        if r_shoulder and r_elbow and r_wrist:
            angle = self.calculate_angle(r_shoulder, r_elbow, r_wrist)
            if angle > 150 and r_wrist[1] < r_shoulder[1]:
                return 'Pointing', 0.75

        # 扇脸/拥抱
        if nose and l_wrist and self.distance(l_wrist, nose) < 0.12:
            if l_wrist[1] < l_shoulder[1] - 0.1:
                return 'Slap face', 0.8
            else:
                return 'Phone', 0.7
        if nose and r_wrist and self.distance(r_wrist, nose) < 0.12:
            if r_wrist[1] < r_shoulder[1] - 0.1:
                return 'Slap face', 0.8
            else:
                return 'Phone', 0.7

        if l_wrist and r_wrist and l_shoulder and r_shoulder:
            arm_span = abs(r_wrist[0] - l_wrist[0])
            shoulder_width = abs(r_shoulder[0] - l_shoulder[0])
            if arm_span > shoulder_width * 1.3:
                shoulder_y = (l_shoulder[1] + r_shoulder[1]) / 2
                hip_y = (l_hip[1] + r_hip[1]) / 2
                if abs(shoulder_y - hip_y) < 0.2:
                    return 'Touch', 0.7
        return 'Unknown', 0.5

    # ---------- 特征提取 ----------
    def extract_skeleton_features(self, keypoints_array):
        features = []
        for j in range(17):
            x = keypoints_array[j, 0]
            y = keypoints_array[j, 1]
            conf = keypoints_array[j, 2]
            if conf < 0.3:
                x, y = 0.5, 0.5
            features.append(x)
            features.append(y)
        return np.array(features)

    def is_valid_skeleton(self, kp_array):
        valid_kpts = 0
        for j in range(17):
            if kp_array[j, 2] > 0.5 and kp_array[j, 0] > 0 and kp_array[j, 1] > 0:
                valid_kpts += 1
        return valid_kpts >= 5

    # ---------- 帧处理 ----------
    def process_frame(self, frame):
        self.frame_count += 1

        if self.frame_count % self.frame_interval != 0:
            if self.last_detection_frame is not None:
                display_frame = frame.copy()
                for result in self.last_detection_results:
                    x1, y1, x2, y2 = map(int, result['box'])
                    action = result['action']
                    track_id = result['track_id']
                    conf = result['confidence']
                    color = self.action_colors.get(action, (0, 255, 0))
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
                    label = f"ID:{track_id} {action} ({conf:.2f})"
                    cv2.putText(display_frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                return display_frame, self.last_detection_results
            return frame, []

        results = self.yolo_model.track(frame, persist=True, verbose=False)[0]
        current_results = []

        if results.boxes is not None and len(results.boxes) > 0:
            boxes = results.boxes.xyxy.cpu().numpy()
            track_ids = results.boxes.id.cpu().numpy().astype(int) if results.boxes.id is not None else range(len(boxes))

            if results.keypoints is not None:
                keypoints_list = results.keypoints.data.cpu().numpy()

                for i, (box, track_id) in enumerate(zip(boxes, track_ids)):
                    kp = keypoints_list[i]
                    kp_array = np.zeros((17, 3))

                    # 卡尔曼滤波
                    if track_id not in self.kalman_filters:
                        self.kalman_filters[track_id] = []
                        for _ in range(17):
                            self.kalman_filters[track_id].append((KalmanFilter1D(), KalmanFilter1D()))
                    for j in range(17):
                        raw_x = kp[j, 0]
                        raw_y = kp[j, 1]
                        kf_x, kf_y = self.kalman_filters[track_id][j]
                        smooth_x = kf_x.update(raw_x)
                        smooth_y = kf_y.update(raw_y)
                        kp_array[j, 0] = smooth_x
                        kp_array[j, 1] = smooth_y
                        kp_array[j, 2] = 1.0

                    if not self.is_valid_skeleton(kp_array):
                        continue

                    features = self.extract_skeleton_features(kp_array)

                    if track_id not in self.keypoints_buffer:
                        self.keypoints_buffer[track_id] = deque(maxlen=self.buffer_size)
                    self.keypoints_buffer[track_id].append(features)

                    action = 'Unknown'
                    conf = 0.5

                    # 混合模型推理
                    if len(self.keypoints_buffer[track_id]) == self.buffer_size and self.lstm_model is not None:
                        sequence = np.array(list(self.keypoints_buffer[track_id]))
                        noise = np.random.normal(0, 0.01, sequence.shape)
                        sequence_tensor = torch.FloatTensor(sequence + noise).unsqueeze(0)

                        with torch.no_grad():
                            output = self.lstm_model(sequence_tensor)
                            probs = torch.softmax(output, dim=1)
                            pred_id = torch.argmax(output, dim=1).item()
                            conf = probs[0][pred_id].item()
                            action = ACTION_ID_TO_NAME.get(pred_id, 'Unknown')

                        # 动作平滑
                        if track_id not in self.action_smooth:
                            self.action_smooth[track_id] = deque(maxlen=self.smooth_window)
                        self.action_smooth[track_id].append(action)
                        action = Counter(self.action_smooth[track_id]).most_common(1)[0][0]

                    # 几何规则辅助（低置信度时）
                    if conf < 0.55 or action in ['Laying', 'Unknown']:
                        rule_action, rule_conf = self.classify_by_geometry(kp_array)
                        if rule_conf > 0.7:
                            if rule_action != action:
                                action = rule_action
                                conf = rule_conf
                            else:
                                conf = max(conf, rule_conf)

                    # 兜底规则
                    if action == 'Unknown':
                        l_shoulder = (kp_array[5,0], kp_array[5,1])
                        r_shoulder = (kp_array[6,0], kp_array[6,1])
                        l_hip = (kp_array[11,0], kp_array[11,1])
                        r_hip = (kp_array[12,0], kp_array[12,1])
                        if l_shoulder and r_shoulder and l_hip and r_hip:
                            body_h = abs((l_hip[1]+r_hip[1])/2 - (l_shoulder[1]+r_shoulder[1])/2)
                            body_w = abs(r_shoulder[0] - l_shoulder[0])
                            if body_w > 0 and body_h / body_w > 1.2:
                                l_wrist = (kp_array[9,0], kp_array[9,1])
                                r_wrist = (kp_array[10,0], kp_array[10,1])
                                arms_low = (l_wrist[1] > l_shoulder[1]-0.05) and (r_wrist[1] > r_shoulder[1]-0.05)
                                if arms_low:
                                    action = 'Stand'
                                    conf = 0.6

                    current_results.append({
                        'track_id': int(track_id),
                        'action': action,
                        'confidence': float(conf),
                        'box': box.tolist()
                    })

                    # 绘制
                    x1, y1, x2, y2 = map(int, box)
                    color = self.action_colors.get(action, (0, 255, 0))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    # 骨架连线
                    for idx1, idx2 in self.skeleton_edges:
                        if kp_array[idx1,2] > 0.5 and kp_array[idx2,2] > 0.5:
                            pt1 = (int(kp_array[idx1,0]), int(kp_array[idx1,1]))
                            pt2 = (int(kp_array[idx2,0]), int(kp_array[idx2,1]))
                            if pt1[0]>0 and pt1[1]>0 and pt2[0]>0 and pt2[1]>0:
                                cv2.line(frame, pt1, pt2, (0,255,0), 2, cv2.LINE_AA)

                    for j in range(17):
                        if kp_array[j,2] > 0.5:
                            cx, cy = int(kp_array[j,0]), int(kp_array[j,1])
                            if cx>0 and cy>0:
                                cv2.circle(frame, (cx, cy), 3, (0,0,255), -1)
                    label = f"ID:{track_id} {action} ({conf:.2f})"
                    cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        self.last_detection_frame = frame.copy()
        self.last_detection_results = current_results
        return frame, current_results

    # ---------- 视频处理 ----------
    def process_video(self, video_path, output_path=None):
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        wait_time = int(1000 / fps)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"视频信息: {width}x{height}, {fps}fps, 总帧数:{total_frames}")

        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        self.frame_count = 0
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            processed_frame, _ = self.process_frame(frame)

            elapsed = time.time() - start_time
            current_fps = self.frame_count / elapsed if elapsed > 0 else 0
            cv2.putText(processed_frame, f"FPS: {current_fps:.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            progress = self.frame_count / total_frames * 100
            cv2.putText(processed_frame, f"Progress: {progress:.1f}%", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            if out:
                out.write(processed_frame)

            cv2.imshow('Pose Action Detection', processed_frame)
            if cv2.waitKey(wait_time) & 0xFF == ord('q'):
                break

        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
        print(f"处理完成! 总帧数:{self.frame_count}, 耗时:{time.time()-start_time:.2f}秒")
        return


if __name__ == "__main__":
    VIDEO_PATH = r"E:\fuchuang\mv1.mp4"          # 待识别视频
    OUTPUT_PATH = None                           # 输出视频路径（可选）
    MODEL_PATH = r"E:\fuchuang\hybrid_models\best_model.pth"  # 训练好的混合模型

    print("=" * 60)
    print("视频行为识别系统（混合模型版：LSTM + Self-Attention）")
    print("=" * 60)
    print(f"视频文件: {VIDEO_PATH}")
    print(f"模型文件: {MODEL_PATH}")
    print("=" * 60)

    detector = VideoActionDetector(model_path=MODEL_PATH)
    detector.process_video(VIDEO_PATH, output_path=OUTPUT_PATH)