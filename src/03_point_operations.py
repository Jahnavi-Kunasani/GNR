import numpy as np
from common import (
    scene_dirs, read_processed_scene, normalize_bands, to_composite,
    save_stack, save_montage, RESULTS_ROOT
)

def negative(x): return 1.0 - x
def log_transform(x): return np.log1p(9.0 * x) / np.log(10.0)
def gamma_transform(x, gamma=0.7): return np.power(np.clip(x, 0, 1), gamma)

def contrast_stretch(x):
    lo, hi = np.percentile(x, [2, 98])
    return np.clip((x - lo) / (hi - lo + 1e-8), 0, 1)

def piecewise_linear(x):
    return np.interp(x, [0, 0.25, 0.75, 1], [0, 0.10, 0.90, 1]).astype(np.float32)

def threshold(x): return (x >= 0.5).astype(np.float32)

def bit_plane_7(x):
    values = np.rint(np.clip(x, 0, 1) * 255).astype(np.uint8)
    return ((values >> 7) & 1).astype(np.float32)

def density_slicing(x):
    classes = np.digitize(x, [0.25, 0.50, 0.75])
    return (classes / 3.0).astype(np.float32)

operations = {
    "negative": negative,
    "log": log_transform,
    "gamma": gamma_transform,
    "contrast_stretch": contrast_stretch,
    "piecewise_linear": piecewise_linear,
    "threshold": threshold,
    "bit_plane_7": bit_plane_7,
    "density_slicing": density_slicing,
}

for scene in scene_dirs():
    raw, profile = read_processed_scene(scene.name)
    data, _ = normalize_bands(raw)
    folder = RESULTS_ROOT / "point_operations" / scene.name
    images, titles = [to_composite(data)], ["Original"]
    for name, operation in operations.items():
        result = np.stack([operation(b) for b in data]).astype(np.float32)
        save_stack(folder / f"{name}.tif", result, profile)
        images.append(to_composite(result))
        titles.append(name.replace("_", " ").title())
    save_montage(folder / "comparison.png", images, titles, cols=3)
    print(f"Point operations completed: {scene.name}")
