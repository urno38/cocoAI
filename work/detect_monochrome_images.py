import os
from PIL import Image
import numpy as np

from common.image import (
    detect_colors_in_image,
    detect_monochrome_images,
    detect_same_size_images,
)


# Exemple d'utilisation
if __name__ == "__main__":
    from pathlib import Path
    from pprint import pprint

    # Exemple d'utilisation
    dossier_images = Path(r"C:\Users\lvolat\Documents\cocoAI\extracted_images2")
    monochrome_images = detect_monochrome_images(dossier_images)
    pprint(monochrome_images)

    reference_image = list(monochrome_images.keys())[1]
    same_size_images = detect_same_size_images(
        dossier_images, dossier_images / reference_image
    )

    for im in same_size_images:
        if im not in list(monochrome_images.keys()):
            num_colors, colors_hex = detect_colors_in_image(dossier_images / im)
            print(f"Nombre de couleurs : {num_colors}")
            print(f"Couleurs : {colors_hex}")

    print(same_size_images)
