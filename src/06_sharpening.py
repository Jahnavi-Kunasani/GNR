import numpy as np
from scipy.ndimage import laplace, sobel, gaussian_filter, convolve
from common import (
    scene_dirs, read_processed_scene, normalize_bands, to_composite,
    save_stack, save_montage, RESULTS_ROOT
)

# Four-neighbour Laplacian mask. Its centre is negative, so f - Laplacian(f)
# sharpens the image, following the convention used in the lecture.
LAPLACIAN_MASK = np.array(
    [[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32
)


def laplacian_sharpen(x, amount=0.6):
    lap = convolve(x, LAPLACIAN_MASK, mode="reflect")
    return np.clip(x - amount * lap, 0, 1)


def sobel_edges(x, amount=0.20):
    """Sobel first-derivative gradient magnitude added to the input band."""
    gx = sobel(x, axis=1, mode="reflect")
    gy = sobel(x, axis=0, mode="reflect")
    magnitude = np.hypot(gx, gy)
    magnitude /= magnitude.max() + 1e-8
    return np.clip(x + amount * magnitude, 0, 1)


def unsharp_mask(x, amount=1.0, sigma=2):
    blurred = gaussian_filter(x, sigma=sigma, mode="reflect")
    mask = x - blurred
    return np.clip(x + amount * mask, 0, 1)


def high_boost(x, k=1.8, sigma=2):
    blurred = gaussian_filter(x, sigma=sigma, mode="reflect")
    mask = x - blurred
    return np.clip(x + k * mask, 0, 1)


operations = {
    "laplacian": laplacian_sharpen,
    "sobel": sobel_edges,
    "unsharp_mask": unsharp_mask,
    "high_boost": high_boost,
}

for scene in scene_dirs():
    raw, profile = read_processed_scene(scene.name)
    data, _ = normalize_bands(raw)
    folder = RESULTS_ROOT / "sharpening" / scene.name
    images, titles = [to_composite(data)], ["Original"]

    for name, operation in operations.items():
        result = np.stack([operation(b) for b in data]).astype(np.float32)
        save_stack(folder / f"{name}.tif", result, profile)
        images.append(to_composite(result))
        titles.append(name.replace("_", " ").title())

    save_montage(folder / "comparison.png", images, titles, cols=3)
    print(f"Sharpening completed: {scene.name}")
