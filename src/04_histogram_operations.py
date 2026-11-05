import numpy as np
from skimage import exposure
from skimage.filters import rank
from common import (
    scene_dirs, read_processed_scene, normalize_bands, to_composite,
    save_stack, save_montage, RESULTS_ROOT
)


def global_equalization(x):
    """Global histogram equalisation of one normalised band."""
    return exposure.equalize_hist(np.clip(x, 0, 1)).astype(np.float32)


def local_histogram_equalization(x, window_size=31):
    """True local histogram equalisation using a moving neighbourhood histogram.

    rank.equalize expects an unsigned integer image, so the normalised band is
    converted to 8-bit for this operation and converted back to [0, 1].
    """
    image_8bit = np.rint(np.clip(x, 0, 1) * 255).astype(np.uint8)
    footprint = np.ones((window_size, window_size), dtype=np.uint8)
    result = rank.equalize(image_8bit, footprint=footprint)
    return (result.astype(np.float32) / 255.0)


def clahe(x):
    """Contrast Limited Adaptive Histogram Equalisation."""
    return exposure.equalize_adapthist(
        np.clip(x, 0, 1), kernel_size= None, clip_limit=0.01
    ).astype(np.float32)


operations = {
    "global_equalization": global_equalization,
    "local_histogram_equalization": local_histogram_equalization,
    "clahe": clahe,
}

for scene in scene_dirs():
    raw, profile = read_processed_scene(scene.name)
    data, _ = normalize_bands(raw)
    folder = RESULTS_ROOT / "histogram_operations" / scene.name
    images, titles = [to_composite(data)], ["Original"]

    for name, operation in operations.items():
        result = np.stack([operation(b) for b in data]).astype(np.float32)
        save_stack(folder / f"{name}.tif", result, profile)
        images.append(to_composite(result))
        titles.append(name.replace("_", " ").title())

    save_montage(folder / "comparison.png", images, titles, cols=2)
    print(f"Histogram operations completed: {scene.name}")
