import rasterio
from common import scene_dirs, raw_band_paths, BANDS

for scene in scene_dirs():
    print(f"\nChecking {scene.name}")
    reference = None
    for band, path in zip(BANDS, raw_band_paths(scene)):
        with rasterio.open(path) as src:
            current = (src.width, src.height, src.crs, src.transform)
            print(f"{band}: {src.width} x {src.height}, dtype={src.dtypes[0]}")
            print(f"    CRS={src.crs}, resolution={src.res}, NoData={src.nodata}")
            if reference is None:
                reference = current
            elif current != reference:
                raise ValueError(f"Grid mismatch: {band} in {scene.name}")
    print("PASS: all four bands are aligned.")
