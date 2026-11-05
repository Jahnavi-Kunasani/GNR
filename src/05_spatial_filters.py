import numpy as np
from scipy.ndimage import (
    uniform_filter, gaussian_filter, median_filter,
    minimum_filter, maximum_filter, generic_filter
)
from common import (
    scene_dirs, read_processed_scene, normalize_bands, to_composite,
    save_stack, save_montage, RESULTS_ROOT
)


WEIGHTED_AVERAGE_MASK = np.array(
    [[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float32
) / 16.0


def weighted_average(x):
    """Weighted 3x3 averaging using the mask shown in the lecture."""
    from scipy.ndimage import convolve
    return convolve(x, WEIGHTED_AVERAGE_MASK, mode="reflect")


def midpoint_filter(x):
    """Midpoint of the local minimum and maximum in a 3x3 window."""
    local_min = minimum_filter(x, size=3, mode="reflect")
    local_max = maximum_filter(x, size=3, mode="reflect")
    return 0.5 * (local_min + local_max)


def _alpha_trimmed_mean(values, d=2):
    """Trim d/2 smallest and d/2 largest values from a 3x3 neighbourhood."""
    ordered = np.sort(values)
    trim = d // 2
    if trim:
        ordered = ordered[trim:-trim]
    return float(np.mean(ordered))


def alpha_trimmed_mean(x, d=2):
    """Alpha-trimmed mean filter; d must be even and between 0 and 8."""
    if d < 0 or d > 8 or d % 2 != 0:
        raise ValueError("d must be an even integer from 0 to 8")
    return generic_filter(
        x, _alpha_trimmed_mean, size=3, mode="reflect", extra_arguments=(d,)
    )


operations = {
    "mean": lambda x: uniform_filter(x, size=3, mode="reflect"),
    "weighted_average": weighted_average,
    "gaussian": lambda x: gaussian_filter(x, sigma=1, mode="reflect"),
    "median": lambda x: median_filter(x, size=3, mode="reflect"),
    "minimum": lambda x: minimum_filter(x, size=3, mode="reflect"),
    "maximum": lambda x: maximum_filter(x, size=3, mode="reflect"),
    "midpoint": midpoint_filter,
    "alpha_trimmed_mean": alpha_trimmed_mean,
}

for scene in scene_dirs():
    raw, profile = read_processed_scene(scene.name)
    data, _ = normalize_bands(raw)
    folder = RESULTS_ROOT / "spatial_filters" / scene.name
    images, titles = [to_composite(data)], ["Original"]

    for name, operation in operations.items():
        result = np.stack([
            np.clip(operation(b), 0, 1) for b in data
        ]).astype(np.float32)
        save_stack(folder / f"{name}.tif", result, profile)
        images.append(to_composite(result))
        titles.append(name.replace("_", " ").title())

    save_montage(folder / "comparison.png", images, titles, cols=3)
    print(f"Spatial filters completed: {scene.name}")
