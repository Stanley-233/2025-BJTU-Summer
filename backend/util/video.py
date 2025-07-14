from PIL import Image
from ultralytics import YOLO

def predict_result(img: Image, model_path: str = "model/RDD_yolov8n_best.pt"):
    model = YOLO(model_path)
    results = model.predict(
        source=img,#自定义测试集路径
        save=True,
    )
    return results
