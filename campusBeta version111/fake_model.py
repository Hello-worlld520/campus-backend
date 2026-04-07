import random

class FakeModel:
    def __init__(self):
        print("假模型加载成功（占位，等真模型替换我）")

    def predict(self, total_frames):
        results = []
        for i in range(0, total_frames, 30):
            action = random.choice(["normal", "fighting", "falling", "smoking", "phone", "loitering"])
            score = round(random.uniform(0.4, 0.95), 2)
            results.append({
                "time_second": round(i / 30, 1),
                "person_id": random.randint(1, 5),
                "behavior": action,
                "score": score,
                "is_alert": score > 0.75 and action != "normal"
            })
        return results 
