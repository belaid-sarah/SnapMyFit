"""
Script pour générer des références automatiques pour toutes les images
basées sur leur catégorie et leur nom de fichier.
"""
import json
from pathlib import Path

def generate_references():
    """Génère image_metadata.json avec des références pour chaque image."""
    labels_file = Path("image_labels.json")
    meta_file = Path("image_metadata.json")
    
    if not labels_file.exists():
        print("❌ image_labels.json n'existe pas. Lancez d'abord categorize_images.py")
        return
    
    # Charger les labels
    with open(labels_file, "r", encoding="utf-8") as f:
        labels = json.load(f)
    
    # Générer les métadonnées avec références
    metadata = {}
    category_counts = {}
    
    for img_path, category in labels.items():
        # Compter les images par catégorie pour générer des refs séquentielles
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
        
        # Générer une référence unique: CATEGORY-XXXX
        ref_num = str(category_counts[category]).zfill(4)
        ref = f"{category.upper()}-{ref_num}"
        
        # Extraire le nom de fichier sans extension
        img_name = Path(img_path).stem
        
        metadata[img_path] = {
            "ref": ref,
            "name": f"{category.capitalize()} {img_name}",
            "category": category,
            "brand": "Unknown",  # À remplir manuellement si besoin
            "price": None  # À remplir manuellement si besoin
        }
    
    # Sauvegarder
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Généré {len(metadata)} références dans {meta_file}")
    print(f"📊 Répartition par catégorie:")
    for cat, count in sorted(category_counts.items()):
        print(f"   {cat}: {count} images")

if __name__ == "__main__":
    generate_references()

