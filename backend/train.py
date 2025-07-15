if __name__ == '__main__':
  from ultralytics import YOLO

  # 定义数据集路径
  dataset_config = 'D:\\China_MotorBike_YOLO\\data.yaml'

  # 加载模型和权重
  model = YOLO('yolo11n.pt')

  # 训练模型，使用早停法，当验证指标在5个epoch内无提升时停止
  results = model.train(
    imgsz=640,
    batch=16,
    epochs=50,
    data=dataset_config,
    name='road_defect_detection',
    project='runs/train',
    patience=5
  )

  print(results)