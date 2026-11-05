from common import (
    scene_dirs, read_raw_scene, normalize_bands, to_composite,
    save_stack, save_rgb, PROCESSED_ROOT
)

for scene in scene_dirs():
    print(f"Preparing {scene.name}...")
    raw_stack, profile = read_raw_scene(scene)
    output_dir = PROCESSED_ROOT / scene.name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save the four original bands together in a georeferenced GeoTIFF.
    save_stack(output_dir / "multispectral.tif", raw_stack, profile)

    # Create display composites from the original data.
    scaled, _ = normalize_bands(raw_stack)
    save_rgb(
        output_dir / "true_colour.png",
        to_composite(scaled, "true"),
        f"{scene.name} — True Colour (B04/B03/B02)"
    )
    save_rgb(
        output_dir / "false_colour.png",
        to_composite(scaled, "false"),
        f"{scene.name} — False Colour (B08/B04/B03)"
    )
    print(f"Saved multispectral.tif, true_colour.png and false_colour.png in {output_dir}")
