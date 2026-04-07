from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import cv2
import yaml
from fake_model import FakeModel
import os

app = FastAPI(title="校园安防视频分析 - 测试版")

# 加载配置
with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 加载假模型
model = FakeModel()

@app.get("/")
def home():
    return {"message": "后端启动成功！现在可以测试上传视频了～"}

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    video_path = os.path.join("uploads", file.filename)
    with open(video_path, "wb") as buffer:
        buffer.write(await file.read())

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "无法打开视频"}

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    skip = config["frame_skip"]
    results = model.predict(frame_count)

    return JSONResponse({
        "filename": file.filename,
        "duration_sec": round(frame_count / fps, 1) if fps > 0 else 0,
        "total_frames": frame_count,
        "results": results,
        "alert_count": sum(1 for r in results if r["is_alert"])
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
