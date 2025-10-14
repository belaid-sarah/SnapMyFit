import os
import cv2
import random

# Chemins dataset DeepFashion
IMG_DIR = "DeepFashion/In-shop Clothes Images/"
BBOX_FILE = "DeepFashion/BBox & Landmark Annotations/list_bbox_inshop.txt"
CAT_FILE = "DeepFashion/Anno/list_category_img.txt"  # peut être dans Attribute Annotations
OUT_DIR = "dataset/"

# Créer structure dossier
os.makedirs(OUT_DIR + "images/train", exist_ok=True)
os.makedirs(OUT_DIR + "images/val", exist_ok=True)
os.makedirs(OUT_DIR + "labels/train", exist_ok=True)
os.makedirs(OUT_DIR + "labels/val", exist_ok=True)

# Charger catégories (img_name -> class_id)
categories = {}
with open(CAT_FILE, "r") as f:
    lines = f.readlines()[2:]  # ignorer header
    for line in lines:
        img_name, cat_id = line.strip().split()
        categories[img_name] = int(cat_id) - 1  # YOLO commence à 0

# Charger bounding boxes (img_name -> bbox)
bboxes = {}
with open(BBOX_FILE, "r") as f:
    lines = f.readlines()[2:]  # ignorer header
    for line in lines:
        parts = line.strip().split()
        img_name = parts[0]
        x_min, y_min, x_max, y_max = map(int, parts[1:])
        bboxes[img_name] = (x_min, y_min, x_max, y_max)

# Split train/val (80/20)
img_list = list(bboxes.keys())
random.shuffle(img_list)
split_idx = int(0.8 * len(img_list))
train_imgs, val_imgs = img_list[:split_idx], img_list[split_idx:]

def convert_yolo(img_path, bbox, class_id):
    img = cv2.imread(img_path)
    if img is None:
        return None
    h, w, _ = img.shape
    x_min, y_min, x_max, y_max = bbox

    # Conversion YOLO
    x_center = (x_min + x_max) / 2 / w
    y_center = (y_min + y_max) / 2 / h
    bw = (x_max - x_min) / w
    bh = (y_max - y_min) / h

    return f"{class_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}\n"

# Sauvegarder images + labels
for img_set, folder in [(train_imgs, "train"), (val_imgs, "val")]:
    for img_name in img_set:
        img_path = os.path.join(IMG_DIR, img_name)
        if not os.path.exists(img_path):
            continue
        
        class_id = categories.get(img_name, 0)
        bbox = bboxes[img_name]

        # Sauvegarde image
        out_img_path = os.path.join(OUT_DIR, "images", folder, img_name)
        os.makedirs(os.path.dirname(out_img_path), exist_ok=True)
        cv2.imwrite(out_img_path, cv2.imread(img_path))

        # Sauvegarde label YOLO
        label_name = img_name.replace(".jpg", ".txt")
        out_label_path = os.path.join(OUT_DIR, "labels", folder, label_name)
        yolo_label = convert_yolo(img_path, bbox, class_id)
        if yolo_label:
            with open(out_label_path, "w") as f:
                f.write(yolo_label)

print("✅ Conversion terminée. Dataset prêt pour YOLO !")
