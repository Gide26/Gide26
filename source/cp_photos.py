"""CarePoint photographic set — licence record, crop and grade."""
import os

import numpy as np
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "assets", "photos")
CACHE_DIR = os.path.join(ROOT, "source", ".work", "cp_photos")

# On perforated film the hole pitch, not the file, limits detail: at 2.3 mm
# centres the mesh resolves roughly 11 holes per inch, so anything much past
# 100 ppi at final size is thrown away by the perforation. Floor and target are
# therefore set by what the medium can actually hold at 1.5 m viewing distance.
MIN_PPI = 75
TARGET_PPI = 100

PHOTOS = {
    "reception": {
        "asset": "PH-01", "src": "src-reception.jpg", "id": 4269206,
        "creator": "Cedric Fauntleroy",
        "url": "https://www.pexels.com/photo/a-receptionist-smiling-at-a-person-4269206/",
        "px": (5474, 8211),
        "title": "Receptionist assisting a patient at a modern reception desk",
        "use": "Entrance / reception",
    },
    "dental": {
        "asset": "PH-02", "src": "src-dental.jpg", "id": 3952130,
        "creator": "Andrea Piacquadio",
        "url": "https://www.pexels.com/photo/dentist-checking-a-patient-s-teeth-3952130/",
        "px": (5760, 3840),
        "title": "Female dentist performing treatment in a modern dental clinic",
        "use": "Dental services",
    },
    "paeds": {
        "asset": "PH-03", "src": "src-paeds.jpg", "id": 5998457,
        "creator": "Pavel Danilyuk",
        "url": "https://www.pexels.com/photo/a-doctor-examining-a-child-patient-5998457/",
        "px": (4016, 6016),
        "title": "Paediatrician examining a child with a stethoscope",
        "use": "Paediatrics",
    },
    "physio": {
        "asset": "PH-04", "src": "src-physio.jpg", "id": 20860597,
        "creator": "Funkcinės Terapijos Centras",
        "url": "https://www.pexels.com/photo/physiotherapist-massaging-leg-and-hip-20860597/",
        "px": (2667, 4000),
        "title": "Physiotherapist treating a patient's leg in a clinic",
        "use": "Physiotherapy",
    },
    "lab": {
        "asset": "PH-05", "src": "src-lab.jpg", "id": 8442574,
        "creator": "Pavel Danilyuk",
        "url": "https://www.pexels.com/photo/woman-doctor-next-to-a-trinocular-microscope-8442574/",
        "px": (5192, 3466),
        "title": "Laboratory technician at a trinocular microscope",
        "use": "Laboratory services",
    },
    "pharmacy": {
        "asset": "PH-06", "src": "src-pharmacy.jpg", "id": 8657370,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/women-looking-at-the-medicine-bottles-at-the-shelves-8657370/",
        "px": (6403, 4269),
        "title": "Pharmacists examining medicine on dispensary shelving",
        "use": "Pharmacy",
    },
    "ultrasound": {
        "asset": "PH-07", "src": "src-us-room.jpg", "id": 7089304,
        "creator": "MART PRODUCTION",
        "url": "https://www.pexels.com/photo/photo-of-ultrasound-scanner-7089304/",
        "px": (6123, 4082),
        "title": "Ultrasound scanner and examination couch in a clinic scanning room",
        "use": "Antenatal services",
        "note": "Equipment only — no patient depicted, so the panel can never be read as a "
                "specific person's scan.",
    },
    "consult": {
        "asset": "PH-08", "src": "src-consult-01.jpg", "id": 7580254,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/doctor-sitting-by-table-with-patient-7580254/",
        "px": (4189, 6284),
        "title": "Doctor consulting a patient across a desk",
        "use": "General medicine",
    },
}


def grade(im, warmth=0.0):
    """Clinical grade tuned for perforated film: slightly cool, deep shadows."""
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(0.88)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    arr = np.asarray(im).astype(np.float32) / 255.0
    luma = arr @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    shadow = np.clip((0.42 - luma) / 0.42, 0, 1)[..., None]
    tint = np.array([0.086, 0.137, 0.247], dtype=np.float32)      # #16233F
    arr = arr * (1 - 0.30 * shadow) + tint * (0.30 * shadow)
    high = np.clip((luma - 0.74) / 0.26, 0, 1)[..., None]
    arr = np.clip(arr + high * 0.04, 0, 1)
    return Image.fromarray((arr * 255).astype(np.uint8))


def prepare(key, w_mm, h_mm, focus=(0.5, 0.4), dpi=110, zoom=1.0):
    """Cover-crop with a stored focus point. Never distorts."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    tag = f"{key}_{int(w_mm)}x{int(h_mm)}_{focus[0]:.2f}{focus[1]:.2f}_{zoom:.2f}"
    out = os.path.join(CACHE_DIR, tag + ".jpg")
    if os.path.exists(out):
        return out

    im = Image.open(os.path.join(SRC_DIR, PHOTOS[key]["src"]))
    im = grade(im)
    sw, sh = im.size
    aspect = w_mm / float(h_mm)

    cw, ch = (sw, sw / aspect) if sw / sh < aspect else (sh * aspect, sh)
    cw, ch = cw / zoom, ch / zoom
    cw, ch = min(cw, sw), min(ch, sh)

    left = (sw - cw) * focus[0]
    top = (sh - ch) * focus[1]
    crop = im.crop((int(left), int(top), int(left + cw), int(top + ch)))

    tw = max(500, int(w_mm / 25.4 * dpi))
    th = max(400, int(h_mm / 25.4 * dpi))
    if crop.width > tw:
        crop = crop.resize((tw, th), Image.LANCZOS)
    crop.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    return out


def ppi(key, w_mm, h_mm, zoom=1.0):
    ow, oh = PHOTOS[key]["px"]
    aspect = w_mm / float(h_mm)
    if ow / oh >= aspect:          # image wider than the pane: height limits
        cw, ch = oh * aspect, oh
    else:                          # image narrower: width limits
        cw, ch = ow, ow / aspect
    cw, ch = cw / zoom, ch / zoom
    d = min(cw / (w_mm / 25.4), ch / (h_mm / 25.4))
    if d >= TARGET_PPI:
        st = "PASS"
    elif d >= MIN_PPI:
        st = "PASS (min)"
    else:
        st = "FAIL"
    return round(d), st
