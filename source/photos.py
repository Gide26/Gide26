"""
Photographic pipeline: deterministic crop, colour grade, resolution audit.

The images in assets/photos are *web preview* files used to build accurate
comps. The licence log records the true pixel dimensions of each original, and
the audit below reports the resolution each panel would achieve in print when
the original file is relinked. Anything under the agreed minimum is flagged so
it can be re-sourced or the crop tightened before output.
"""
import os
import json

import numpy as np
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "assets", "photos")
CACHE_DIR = os.path.join(ROOT, "source", ".work", "photocache")

# Agreed large-format thresholds (PROVISIONAL — confirm with the printer).
MIN_DPI = 110       # absolute floor at final size, viewing distance >= 1.2 m
TARGET_DPI = 150    # preferred

PHOTOS = {
    "reception": {
        "src": "src-reception.jpg",
        "asset": "A-01",
        "pexels_id": 4269206,
        "creator": "Cedric Fauntleroy",
        "url": "https://www.pexels.com/photo/a-receptionist-smiling-at-a-person-4269206/",
        "original_px": (5474, 8211),
        "title": "A receptionist smiling at a person (reception desk, tablet)",
    },
    "consult_01": {
        "src": "src-consult-01.jpg",
        "asset": "A-02",
        "pexels_id": 7580254,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/doctor-sitting-by-table-with-patient-7580254/",
        "original_px": (4189, 6284),
        "title": "Doctor sitting by table with patient",
    },
    "consult_02": {
        "src": "src-consult-02.jpg",
        "asset": "A-03",
        "pexels_id": 5327864,
        "creator": "Thirdman",
        "url": "https://www.pexels.com/photo/5327864/",
        "original_px": (4231, 6346),
        "title": "Medical professional sitting on a chair holding a tablet while talking",
    },
    "lab": {
        "src": "src-lab.jpg",
        "asset": "A-04",
        "pexels_id": 8442574,
        "creator": "Pavel Danilyuk",
        "url": "https://www.pexels.com/photo/woman-doctor-next-to-a-trinocular-microscope-8442574/",
        "original_px": (5192, 3466),
        "title": "Woman lab technician examining samples with a trinocular microscope",
    },
    "pharmacy": {
        "src": "src-pharmacy.jpg",
        "asset": "A-05",
        "pexels_id": 8657370,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/women-looking-at-the-medicine-bottles-at-the-shelves-8657370/",
        "original_px": (6403, 4269),
        "title": "Pharmacists examining medicine bottles on a pharmacy shelf",
    },
    "imaging": {
        "src": "src-imaging.jpg",
        "asset": "A-06",
        "pexels_id": 7089017,
        "creator": "MART PRODUCTION",
        "url": "https://www.pexels.com/photo/technology-hospital-medicine-indoors-7089017/",
        "original_px": (6000, 4000),
        "title": "MRI scanner in a hospital imaging room",
    },
}


def _grade(im):
    """Restrained clinical grade: cooler shadows, controlled contrast, calm colour."""
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(0.84)
    im = ImageEnhance.Contrast(im).enhance(1.07)
    arr = np.asarray(im).astype(np.float32) / 255.0

    luma = arr @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    # shadow mask: strongest in the darkest 45% of the image
    shadow = np.clip((0.45 - luma) / 0.45, 0, 1)[..., None]
    navy_tint = np.array([0.031, 0.129, 0.239], dtype=np.float32)   # #08213D
    arr = arr * (1 - 0.26 * shadow) + navy_tint * (0.26 * shadow)

    # gentle highlight lift so white coats do not clip flat
    high = np.clip((luma - 0.72) / 0.28, 0, 1)[..., None]
    arr = arr + high * 0.045

    arr = np.clip(arr, 0, 1)
    # soft S-curve
    arr = arr * arr * (3 - 2 * arr) * 0.35 + arr * 0.65
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


def prepare(key, width_mm, height_mm, focus=(0.5, 0.42), dpi=120, grade=True):
    """Crop + grade a photograph for a specific print window.

    focus = (x, y) normalised position in the SOURCE image that should sit at
    (x, y) of the crop window. This is the deliberate crop control: it keeps
    faces and equipment where the grid needs them and never distorts.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    meta = PHOTOS[key]
    aspect = width_mm / height_mm
    cache = os.path.join(
        CACHE_DIR, f"{key}_{int(width_mm)}x{int(height_mm)}_{focus[0]:.2f}-{focus[1]:.2f}_{dpi}.jpg")
    if os.path.exists(cache):
        return cache

    im = Image.open(os.path.join(SRC_DIR, meta["src"])).convert("RGB")
    if grade:
        im = _grade(im)

    sw, sh = im.size
    # cover-crop to the window aspect
    if sw / sh > aspect:
        new_h = sh
        new_w = int(round(sh * aspect))
        max_x = sw - new_w
        left = int(round(max_x * focus[0]))
        top = 0
    else:
        new_w = sw
        new_h = int(round(sw / aspect))
        max_y = sh - new_h
        left = 0
        top = int(round(max_y * focus[1]))
    crop = im.crop((left, top, left + new_w, top + new_h))

    target_px = max(600, int(round(width_mm / 25.4 * dpi)))
    target_py = max(400, int(round(height_mm / 25.4 * dpi)))
    if crop.width > target_px:
        crop = crop.resize((target_px, target_py), Image.LANCZOS)

    crop.save(cache, "JPEG", quality=84, optimize=True, progressive=True)
    return cache


def audit(key, width_mm, height_mm, focus):
    """Effective print resolution of the ORIGINAL file for this crop window."""
    ow, oh = PHOTOS[key]["original_px"]
    aspect = width_mm / height_mm
    # replicate the cover-crop maths in source pixels
    if ow / oh > aspect:
        crop_w = oh * aspect
        crop_h = oh
    else:
        crop_w = ow
        crop_h = ow / aspect
    dpi_w = crop_w / (width_mm / 25.4)
    dpi_h = crop_h / (height_mm / 25.4)
    dpi = min(dpi_w, dpi_h)
    if dpi >= TARGET_DPI:
        status = "PASS"
    elif dpi >= MIN_DPI:
        status = "PASS (acceptable)"
    else:
        status = "FAIL — tighten crop"
    return {
        "effective_dpi": round(dpi, 1),
        "status": status,
        "crop_px": (int(round(crop_w)), int(round(crop_h))),
        "required_px_at_150": (int(round(width_mm / 25.4 * 150)),
                              int(round(height_mm / 25.4 * 150))),
    }


def contact_sheet_cache():
    return CACHE_DIR


if __name__ == "__main__":
    print(json.dumps({k: audit(k, 1000, 960, (0.5, 0.42)) for k in PHOTOS}, indent=2))
