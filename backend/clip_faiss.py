from pathlib import Path
import shutil
from . import search_engine

# Script utilitaire léger qui s'appuie sur search_engine

def run_demo(query: str = "test.jpg", k: int = 5):
    results = search_engine.search_image(query, k=k)
    print(f"\n🔎 Résultats similaires pour {query} :")
    for r in results:
        print("   ", r)

    # Sauvegarde des résultats
    query_name = Path(query).stem
    save_dir = Path("results") / query_name
    save_dir.mkdir(parents=True, exist_ok=True)
    for r in results:
        shutil.copy(r, save_dir / Path(r).name)
    print(f"\n✅ {len(results)} images copiées dans : {save_dir.resolve()}")

if __name__ == "__main__":
    run_demo()
