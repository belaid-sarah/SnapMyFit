from ultralytics import YOLO
import cv2

# 1. Charger le modèle YOLO pré-entraîné (sur COCO)
model = YOLO("yolov8s.pt")

# 2. Choisir une image (télécharge une photo de mode par exemple "test.jpg")
image_path = "test.jpg"  # mets le chemin vers ton image

# 3. Faire une prédiction
results = model.predict(image_path, save=True, conf=0.25)

# 4. Afficher les classes détectées
for r in results:
    for c in r.boxes.cls:
        print("Classe prédite :", model.names[int(c)])

print("✅ Résultats sauvegardés dans runs/detect/predict/")
