import os
import shutil
from pathlib import Path
import argparse

import search_engine


def list_root_images(images_dir: Path):
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    for f in images_dir.iterdir():
        if f.is_file() and f.suffix.lower() in exts:
            yield f


def ensure_class_folder(images_dir: Path, cls: str) -> Path:
    dst_dir = images_dir / cls
    dst_dir.mkdir(parents=True, exist_ok=True)
    return dst_dir


def move_image_to_class(img_path: Path, cls: str, dry_run: bool = False) -> Path:
    images_dir = img_path.parent
    dst_dir = ensure_class_folder(images_dir, cls)
    dst_path = dst_dir / img_path.name
    if dry_run:
        print(f"[DRY-RUN] Would move {img_path} -> {dst_path}")
        return dst_path
    shutil.move(str(img_path), str(dst_path))
    return dst_path


def categorize(images_root: str, dry_run: bool = False):
    images_dir = Path(images_root)
    if not images_dir.exists():
        raise FileNotFoundError(f"Images folder not found: {images_root}")

    # Init CLIP (search_engine will lazy-init)
    search_engine.initialize()

    moved = 0
    total = 0
    for img in list_root_images(images_dir):
        total += 1
        cls = search_engine.get_type_of_image(str(img))
        dst = move_image_to_class(img, cls, dry_run=dry_run)
        if not dry_run:
            moved += 1
            # Persist label
            if search_engine.image_labels is not None:
                search_engine.image_labels[str(dst)] = cls

    # Sauvegarder labels
    if not dry_run and search_engine.image_labels is not None:
        metadata_dir = images_dir.parent / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        with open(metadata_dir / "image_labels.json", "w", encoding="utf-8") as f:
            import json
            json.dump(search_engine.image_labels, f)

    print(f"Processed {total} files. {'Moved ' + str(moved) if not dry_run else 'No files moved (dry-run)'}.")


def main():
    parser = argparse.ArgumentParser(description="Auto-categorize images into class folders using CLIP.")
    parser.add_argument("--images", default="images", help="Path to images root folder")
    parser.add_argument("--dry-run", action="store_true", help="Do not move files, only print actions")
    args = parser.parse_args()

    categorize(args.images, dry_run=args.dry_run)


if __name__ == "__main__":
    main()


