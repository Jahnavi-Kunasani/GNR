# GNR401 – Spatial-Domain Image Enhancement

A satellite image processing project implementing spatial-domain image enhancement techniques on multispectral satellite imagery.

## 1. Prerequisites

- Python 3
- GNU Make
- Git

## 2. Clone the Repository

```bash
git clone https://github.com/Jahnavi-Kunasani/GNR.git
cd GNR
```

## 3. Download the Input Satellite Data

**Important:** The original satellite images are not included in this GitHub repository because the JP2 files are large.

You must obtain the input satellite data separately before running the project.

The project requires four bands for each scene:

- B02 – Blue
- B03 – Green
- B04 – Red
- B08 – Near Infrared (NIR)

### Required Directory Structure

Place the downloaded JP2 files in the following structure:

```text
GNR/
└── data/
    └── raw/
        ├── scene_1/
        │   ├── B02.jp2
        │   ├── B03.jp2
        │   ├── B04.jp2
        │   └── B08.jp2
        │
        ├── scene_2/
        │   ├── B02.jp2
        │   ├── B03.jp2
        │   ├── B04.jp2
        │   └── B08.jp2
        │
        ├── scene_3/
        │   ├── B02.jp2
        │   ├── B03.jp2
        │   ├── B04.jp2
        │   └── B08.jp2
        │
        └── scene_4/
            ├── B02.jp2
            ├── B03.jp2
            ├── B04.jp2
            └── B08.jp2
```

Each scene must contain all four aligned bands with the expected filenames.

The `data/raw/` directory is excluded from Git tracking. Your downloaded satellite images will remain local and will not be uploaded when you push changes to GitHub.

## 4. Run the Project

From the project root directory, execute:

```bash
make run
```

The Makefile automatically:

1. Creates a Python virtual environment (`.venv`) if required.
2. Upgrades pip.
3. Installs dependencies from `requirements.txt`.
4. Runs the complete image-processing pipeline sequentially.

No manual virtual environment creation or dependency installation is required.

## 5. Processing Pipeline

The complete pipeline executes the following stages:

| Stage | Script | Description |
|---|---|---|
| 1 | `01_check_data.py` | Validate input data |
| 2 | `02_prepare_data.py` | Generate multispectral TIFF and TCC/FCC previews |
| 3 | `03_point_operations.py` | Point-operation enhancement |
| 4 | `04_histogram_operations.py` | Histogram enhancement |
| 5 | `05_spatial_filters.py` | Spatial filtering |
| 6 | `06_sharpening.py` | Sharpening and edge enhancement |

Each stage runs only after the previous stage completes successfully.

## 6. Individual Commands

The Makefile also supports running individual stages:

```bash
make setup
make check
make prepare
make point
make histogram
make filters
make sharpening
```

To execute the complete pipeline:

```bash
make run
```

To see all available commands:

```bash
make help
```

## 7. Output Directories

Generated intermediate data is stored in:

```text
data/processed/
```

Final enhancement outputs are organized under:

```text
results/
├── point_operations/
├── histogram_operations/
├── spatial_filters/
└── sharpening/
```

These directories are created and populated during processing.

## 8. Cleaning Generated Files

To remove generated intermediate data and result files:

```bash
make clean
```

This does not delete the original satellite images inside `data/raw/`, source code, or the Python virtual environment.

## 9. Project Structure

```text
GNR/
├── data/
│   ├── raw/                  # Download separately
│   └── processed/            # Generated automatically
│
├── results/                  # Enhancement outputs
│
├── src/
│   ├── 01_check_data.py
│   ├── 02_prepare_data.py
│   ├── 03_point_operations.py
│   ├── 04_histogram_operations.py
│   ├── 05_spatial_filters.py
│   └── 06_sharpening.py
│
├── Makefile
├── requirements.txt
├── README.md
└── .gitignore
```
