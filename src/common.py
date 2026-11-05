from pathlib import Path
import numpy as np
import rasterio
import matplotlib.pyplot as plt

BANDS = ["B02", "B03", "B04", "B08"]
RAW_ROOT = Path("data/raw")
PROCESSED_ROOT = Path("data/processed")
RESULTS_ROOT = Path("results")

USE_CROP = True
WINDOW_SIZE = 2048
WINDOW_ROW = 4000
WINDOW_COL = 4000

def scene_dirs():
    if not RAW_ROOT.exists():
        raise FileNotFoundError("Create data/raw/scene_1 and place B02.jp2, B03.jp2, B04.jp2, B08.jp2 inside it.")
    dirs = sorted(p for p in RAW_ROOT.iterdir() if p.is_dir())
    if not dirs:
        raise FileNotFoundError("No scene folders found under data/raw/.")
    return dirs

def raw_band_paths(scene_dir):
    paths = [scene_dir / f"{band}.jp2" for band in BANDS]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing input file(s): " + ", ".join(missing))
    return paths

def read_raw_scene(scene_dir):
    paths = raw_band_paths(scene_dir)
    arrays, profiles = [], []
    out_transform = None

    for i, path in enumerate(paths):
        with rasterio.open(path) as src:
            profiles.append(src.profile.copy())
            if USE_CROP:
                row = min(WINDOW_ROW, max(0, src.height - WINDOW_SIZE))
                col = min(WINDOW_COL, max(0, src.width - WINDOW_SIZE))
                height = min(WINDOW_SIZE, src.height - row)
                width = min(WINDOW_SIZE, src.width - col)
                window = rasterio.windows.Window(col, row, width, height)
                arrays.append(src.read(1, window=window).astype(np.float32))
                if i == 0:
                    out_transform = rasterio.windows.transform(window, src.transform)
            else:
                arrays.append(src.read(1).astype(np.float32))
                if i == 0:
                    out_transform = src.transform

    ref = profiles[0]
    for band, profile in zip(BANDS[1:], profiles[1:]):
        for key in ("width", "height", "crs", "transform"):
            if ref[key] != profile[key]:
                raise ValueError(f"{band} is not aligned with B02 in {scene_dir.name}.")

    stack = np.stack(arrays, axis=0)
    out_profile = ref.copy()
    out_profile.update(
        driver="GTiff", count=4, width=stack.shape[2], height=stack.shape[1],
        transform=out_transform, dtype="float32", compress="deflate", predictor=3
    )
    return stack, out_profile

def read_processed_scene(scene_name):
    path = PROCESSED_ROOT / scene_name / "multispectral.tif"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run `python src/02_prepare_data.py` first."
        )
    with rasterio.open(path) as src:
        data = src.read().astype(np.float32)
        profile = src.profile.copy()
    return data, profile

def normalize_bands(data, limits=None):
    if limits is None:
        limits = []
        for band in data:
            lo, hi = np.nanpercentile(band, [2, 98])
            if hi <= lo:
                hi = lo + 1.0
            limits.append((float(lo), float(hi)))
    scaled = np.empty(data.shape, dtype=np.float32)
    for i, (lo, hi) in enumerate(limits):
        scaled[i] = np.clip((data[i] - lo) / (hi - lo), 0, 1)
    return scaled, limits

def apply_display_limits(data, limits):
    scaled = np.empty(data.shape, dtype=np.float32)
    for i, (lo, hi) in enumerate(limits):
        scaled[i] = np.clip((data[i] - lo) / (hi - lo + 1e-8), 0, 1)
    return scaled

def to_composite(stack, kind="true"):
    # Input band order: B02, B03, B04, B08.
    indices = [2, 1, 0] if kind == "true" else [3, 2, 1]
    return np.stack([stack[i] for i in indices], axis=-1)

def save_rgb(path, rgb, title):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(np.clip(rgb, 0, 1))
    ax.set_title(title)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)

def save_stack(path, stack, profile):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    p = profile.copy()
    p.update(driver="GTiff", count=4, dtype="float32",
             compress="deflate", predictor=3)
    with rasterio.open(path, "w", **p) as dst:
        dst.write(stack.astype(np.float32))

def save_montage(path, images, titles, cols=3):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = int(np.ceil(len(images) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4.5 * rows))
    axes = np.asarray(axes).reshape(-1)
    for ax, image, title in zip(axes, images, titles):
        ax.imshow(np.clip(image, 0, 1))
        ax.set_title(title)
        ax.axis("off")
    for ax in axes[len(images):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
