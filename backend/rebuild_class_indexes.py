"""
Script pour reconstruire les index FAISS par classe basés sur image_labels.json
Cela accélère la recherche en permettant de chercher uniquement dans la classe pertinente.
"""
import json
from pathlib import Path
import search_engine

def rebuild_class_indexes():
    """Reconstruit les index FAISS par classe."""
    print("🔄 Reconstruction des index par classe...")
    
    # Initialiser le moteur de recherche (charge les labels et construit les index)
    search_engine.initialize()
    
    print("✅ Index par classe reconstruits et prêts !")
    print(f"📊 Classes disponibles: {list(search_engine.class_to_index.keys())}")
    for cls, idx in search_engine.class_to_index.items():
        count = search_engine.class_to_indices.get(cls, [])
        print(f"   {cls}: {len(count)} images, index: faiss_index_{cls}.bin")

if __name__ == "__main__":
    rebuild_class_indexes()

