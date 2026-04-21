# campus-backend说明文档

## 一、项目简介

基于 YOLOv8 + Flask 的智能校园安防监控系统。

### 核心功能

| 功能             | 说明                      |
| :--------------- | :------------------------ |
| 实时摄像头监控   | 支持本地USB摄像头         |
| RTSP网络摄像头   | 支持海康/大华等网络摄像头 |
| 本地视频上传检测 | 用户上传视频进行AI分析    |
| 人员/车辆识别    | YOLOv8 80种物体检测       |
| 打架行为告警     | 两人距离过近自动报警      |
| 多路并发         | 同时处理多个视频源        |

------

## 二、系统要求

| 项目       | 要求                        |
| :--------- | :-------------------------- |
| 操作系统   | Windows 10/11               |
| 内存       | 8GB以上（推荐）             |
| 存储空间   | 5GB以上                     |
| Python版本 | 3.9                         |
| 摄像头     | USB摄像头或笔记本内置摄像头 |

------

## 三、安装部署

### 3.1 安装 Anaconda

1. 访问官网下载：https://www.anaconda.com/download
2. 选择 Windows 64-bit 版本
3. 双击安装，**勾选** "Add Anaconda to my PATH environment variable"
4. 安装完成后，打开 **Anaconda Prompt** 验证：



```
conda --version
```



### 3.2 创建虚拟环境

在 Anaconda Prompt 中执行：



```
conda create -n campus_security python=3.9 -y
```



激活环境：



```
conda activate campus_security
```



看到命令行前面出现 `(campus_security)` 表示成功。

### 3.3 安装依赖包



```
pip install opencv-python flask flask-cors torch torchvision ultralytics pillow
```



等待安装完成（约 2-5 分钟）。

### 3.4 验证安装



```
python -c "import cv2; print('OpenCV OK'); import flask; print('Flask OK'); import torch; print('PyTorch OK'); from ultralytics import YOLO; print('YOLO OK')"
```



看到 4 个 OK 表示安装成功。

### 3.5 准备模型文件

将训练好的 `best.pt` 模型文件放入 `models/` 目录：



```
项目目录/
├── models/
│   └── best.pt
├── config.py
├── app.py
└── temp/
```



**注意：** 如果没有模型文件，系统会报错无法启动。

------

## 四、启动服务

### 4.1 启动步骤

**每次启动都需要执行以下命令：**



```
# 第1步：打开 Anaconda Prompt

# 第2步：激活虚拟环境
conda activate campus_security

# 第3步：进入项目目录
cd Desktop\campus_security_backend

# 第4步：启动服务
python app.py
```



### 4.2 启动成功标志

看到以下信息表示启动成功：



```
==================================================
 启动成功！
==================================================
本地访问：http://127.0.0.1:5000
 外部访问：http://192.168.1.100:5000

 测试接口：
   http://127.0.0.1:5000/status

 视频流测试：
   http://127.0.0.1:5000/video_feed?source=0

  按 Ctrl+C 停止服务
==================================================
```



### 4.3 停止服务

在命令行窗口按 `Ctrl + C`

------

## 五、使用说明

### 5.1 使用电脑摄像头

1. 启动服务
2. 浏览器打开：`http://127.0.0.1:5000/video_feed?source=0`
3. 看到带检测框的实时画面

### 5.2 使用外接摄像头

浏览器打开：`http://127.0.0.1:5000/video_feed?source=1`

### 5.3 使用RTSP网络摄像头

浏览器打开：`http://127.0.0.1:5000/video_feed?source=rtsp://摄像头地址`

### 5.4 手机查看监控

1. 确保手机和电脑在同一WiFi
2. 启动服务后查看电脑IP地址
3. 手机浏览器打开：`http://电脑IP:5000/video_feed?source=0`

### 5.5 上传视频分析

前端通过POST请求上传视频文件：



```
const formData = new FormData();
formData.append('video', file);

fetch('http://127.0.0.1:5000/upload_video', {
    method: 'POST',
    body: formData
})
.then(response => {
    document.getElementById('video').src = response.url;
});
```



### 5.6 停止检测

停止指定流：`http://127.0.0.1:5000/stop?source_id=stream_0`

停止所有流：`http://127.0.0.1:5000/stop_all`

------

## 六、配置说明

### config.py 配置文件



```
# 模型配置
MODEL_PATH = "models/best.pt"      # 模型文件路径

# 检测参数
CONF_THRESHOLD = 0.5               # 置信度阈值（0-1，越高越严格）
IOU_THRESHOLD = 0.45               # IOU阈值
DETECTION_INTERVAL = 2             # 检测间隔（每2帧检测一次）

# 性能配置
FPS_LIMIT = 20                     # 帧率限制

# 服务器配置
HOST = "0.0.0.0"                   # 监听地址
PORT = 5000                        # 端口号
```



### 参数说明

| 参数               | 说明                           | 建议值 |
| :----------------- | :----------------------------- | :----- |
| CONF_THRESHOLD     | 置信度阈值，低于此值不显示     | 0.5    |
| DETECTION_INTERVAL | 检测间隔，越大性能越好但响应慢 | 2-4    |
| FPS_LIMIT          | 帧率限制，越低CPU占用越低      | 15-30  |

------

## 七、常见问题

### Q1: 提示 "No module named 'cv2'"

**解决方案：**



```
pip install opencv-python
```



### Q2: 摄像头无法打开

**原因：** 摄像头被其他程序占用（QQ、微信、Zoom等）

**解决方案：** 关闭占用摄像头的程序

### Q3: 模型加载失败

**原因：** `models/best.pt` 文件不存在

**解决方案：** 将训练好的模型文件放入 `models/` 目录

### Q4: 端口5000被占用

**解决方案：** 修改 `config.py` 中的端口号



```
PORT = 5001
```



### Q5: 安装依赖速度慢

**解决方案：** 使用清华镜像



```
pip install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple
```



### Q6: 检测速度慢

**优化方案：**

- 降低 `FPS_LIMIT`（如改为10）
- 提高 `DETECTION_INTERVAL`（如改为4）

### Q7: 视频上传后看不到分析结果

**检查：**

- 确认视频格式为 mp4/avi/mov
- 查看控制台是否有错误信息
- 检查 `temp/` 目录是否有写入权限

------

## 八、文件结构



```
campus_security_backend/
│
├── app.py              # 主程序（Flask应用）
├── config.py           # 配置文件
├── start.bat           # 启动脚本（可选）
│
├── models/
│   └── best.pt         # YOLO模型文件
│
├── temp/               # 临时文件目录（自动创建）
│
└── README.md           # 本说明文档
```



------

## 九、告警说明

系统会自动检测打架行为并在视频流中标注：

| 告警类型 | 触发条件            | 画面显示                               |
| :------- | :------------------ | :------------------------------------- |
| 打架行为 | 两人距离小于150像素 | 画面顶部红色横幅显示"检测到打架行为！" |

------

## 十、技术支持

如遇问题，请检查：

1. ✅ Anaconda是否正确安装
2. ✅ 虚拟环境是否激活（命令行有 `(campus_security)`）
3. ✅ 模型文件是否存在
4. ✅ 摄像头是否被其他程序占用
5. ✅ 端口是否被占用