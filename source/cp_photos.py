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
        "creator": "Funkcines Terapijos Centras",
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
    "hiv": {
        "asset": "PH-09", "src": "src-hiv-test.jpg", "id": 6074931,
        "creator": "Alena Shekhovtcova",
        "url": "https://www.pexels.com/photo/unrecognizable-laboratory-worker-showing-blood-test-tubes-6074931/",
        "px": (4160, 6240),
        "title": "Gloved hand holding two blood sample tubes for testing",
        "use": "HIV testing",
        "note": "Specimen only — no patient, no face, no result shown, so the pane can never be "
                "read as anyone's status.",
    },
    "cbc": {
        "asset": "PH-10", "src": "src-cbc.jpg", "id": 8460340,
        "creator": "Los Muertos Crew",
        "url": "https://www.pexels.com/photo/a-person-holding-vacutainer-8460340/",
        "px": (6000, 4000),
        "title": "Gloved hands handling a purple-top blood tube over a vacutainer rack",
        "use": "CBC / full blood count",
        "note": "Hands only — no face, which keeps a blood-draw image clinical rather than "
                "personal.",
    },
    "malaria": {
        "asset": "PH-11", "src": "src-malaria.jpg", "id": 32946369,
        "creator": "Saeed Saeed",
        "url": "https://www.pexels.com/photo/macro-shot-of-mosquito-on-human-skin-in-kaduna-32946369/",
        "px": (2795, 4466),
        "title": "Macro photograph of a mosquito on skin, taken in Kaduna, Nigeria",
        "use": "Malaria testing",
    },
    "consult": {
        "asset": "PH-08", "src": "src-consult-01.jpg", "id": 7580254,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/doctor-sitting-by-table-with-patient-7580254/",
        "px": (4189, 6284),
        "title": "Doctor consulting a patient across a desk",
        "use": "General medicine",
    },
    # ---- doors 2 and 3 (added 29 Oct 2026) -----------------------------------
    "consult_bp": {
        "asset": "PH-12", "src": "src-consult-bp.jpg", "id": 5721672,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/a-healthcare-worker-measuring-her-own-blood-pressure-using-a-sphygmomanometer-5721672/",
        "px": (4132, 6198),
        "title": "Nurse taking a blood pressure reading with a digital monitor",
        "use": "General consultation",
    },
    "immunisation": {
        "asset": "PH-13", "src": "src-vaccines.jpg", "id": 13060613,
        "creator": "Lucas Guimar\u00e3es Bueno",
        "url": "https://www.pexels.com/photo/pieces-of-opened-vials-on-stainless-tray-13060613/",
        "px": (5472, 3648),
        "title": "Opened vials and a syringe on a stainless tray",
        "use": "Immunisation",
        "note": "Vials and syringe only \u2014 labels are out of focus, no patient, no dose shown.",
    },
    "surgery": {
        "asset": "PH-14", "src": "src-surgery.jpg", "id": 6291179,
        "creator": "Anna Shvets",
        "url": "https://www.pexels.com/photo/clos-up-of-surgical-instruments-6291179/",
        "px": (3835, 5752),
        "title": "Surgical instruments laid out on a sterile table",
        "use": "Minor surgery",
        "note": "Instruments only — no patient, no wound, no procedure in progress.",
    },
    "cbc_rack": {
        "asset": "PH-15", "src": "src-cbc-rack.jpg", "id": 6627696,
        "creator": "Karola G",
        "url": "https://www.pexels.com/photo/2-vacutainer-on-the-rack-6627696/",
        "px": (4480, 6720),
        "title": "Blood sample tubes in a rack beside a centrifuge",
        "use": "CBC / full blood count",
        "note": "Specimen only — no patient, no face, no result.",
    },
    "lab_micro": {
        "asset": "PH-16", "src": "src-lab-micro.jpg", "id": 9768447,
        "creator": "Ron Lach",
        "url": "https://www.pexels.com/photo/a-female-scientist-looking-through-microscope-9768447/",
        "px": (2987, 4480),
        "title": "Scientist working at a microscope",
        "use": "Laboratory",
    },
    "pharmacy_counter": {
        "asset": "PH-17", "src": "src-pharmacy-counter.jpg", "id": 8657358,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/a-man-handing-a-pump-bottle-to-a-woman-8657358/",
        "px": (6720, 4480),
        "title": "Pharmacist handing medicine across a dispensary counter",
        "use": "Pharmacy",
    },
    "hiv_selftest": {
        "asset": "PH-18", "src": "src-hiv-selftest.jpg", "id": 5712679,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/doing-a-self-test-for-hiv-5712679/",
        "px": (5929, 3953),
        "title": "Hands preparing a rapid test kit on a white table",
        "use": "HIV testing",
        "note": "Hands and kit only — no face, no result, so the pane can never be read as "
                "anyone's status.",
    },
    "antenatal_consult": {
        "asset": "PH-19", "src": "src-antenatal-consult.jpg", "id": 7089401,
        "creator": "MART PRODUCTION",
        "url": "https://www.pexels.com/photo/people-woman-sitting-technology-7089401/",
        "px": (6000, 4000),
        "title": "Doctor consulting a pregnant patient",
        "use": "Antenatal care",
    },
    "pharmacy_shelf": {
        "asset": "PH-20", "src": "src-pharmacy-shelf.jpg", "id": 8657295,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/female-pharmacist-getting-medicines-on-a-cabinet-8657295/",
        "px": (6601, 4401),
        "title": "Pharmacist arranging bottles in a dispensary cabinet",
        "use": "Pharmacy",
    },
    "lab_scientist": {
        "asset": "PH-21", "src": "src-lab-scientist.jpg", "id": 8851548,
        "creator": "Mikhail Nilov",
        "url": "https://www.pexels.com/photo/scientist-looking-through-microscope-8851548/",
        "px": (7952, 5304),
        "title": "Scientist examining samples at a microscope",
        "use": "Laboratory",
    },
    "surgery_tools": {
        "asset": "PH-22", "src": "src-surgery-tools.jpg", "id": 7108125,
        "creator": "Pavel Danilyuk",
        "url": "https://www.pexels.com/photo/sterile-surgical-equipment-7108125/",
        "px": (3654, 5473),
        "title": "Surgical tools arranged on a sterile surface",
        "use": "Minor surgery",
        "note": "Instruments only — no patient and no procedure shown.",
    },
    "cbc_rack_2": {
        "asset": "PH-23", "src": "src-cbc-rack-2.jpg", "id": 6627697,
        "creator": "Karola G",
        "url": "https://www.pexels.com/photo/2-vacutainer-with-blood-samples-6627697/",
        "px": (6580, 4387),
        "title": "Blood samples in a rack with a centrifuge",
        "use": "CBC / full blood count",
        "note": "Specimen only — no patient, no face, no result.",
    },
    "ultrasound_exam": {
        "asset": "PH-24", "src": "src-ultrasound-exam.jpg", "id": 7088826,
        "creator": "MART PRODUCTION",
        "url": "https://www.pexels.com/photo/people-woman-sitting-technology-7088826/",
        "px": (5625, 3750),
        "title": "Ultrasound examination of a pregnant patient",
        "use": "Ultrasound",
    },
    "scan_room": {
        "asset": "PH-25", "src": "src-scan-room.jpg", "id": 7089041,
        "creator": "MART PRODUCTION",
        "url": "https://www.pexels.com/photo/woman-technology-computer-doctor-7089041/",
        "px": (3949, 5923),
        "title": "Clinician operating an ultrasound scanner in a clinic room",
        "use": "Antenatal care",
    },
    "scan_obgyn": {
        "asset": "PH-26", "src": "src-scan-obgyn.jpg", "id": 7089394,
        "creator": "MART PRODUCTION",
        "url": "https://www.pexels.com/photo/photo-of-an-ob-gyn-sitting-beside-ultrasound-machine-7089394/",
        "px": (3982, 5973),
        "title": "OB-GYN beside the ultrasound machine, scan on the monitor",
        "use": "Ultrasound",
    },
    "pharm_handover": {
        "asset": "PH-27", "src": "src-pharm-handover.jpg", "id": 8657359,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/a-man-giving-a-small-black-bottle-to-the-woman-8657359/",
        "px": (6091, 4061),
        "title": "Pharmacist handing dispensed medicine across the counter",
        "use": "Pharmacy",
    },
    "tablets_hands": {
        "asset": "PH-28", "src": "src-tablets-hands.jpg", "id": 3923159,
        "creator": "cottonbro studio",
        "url": "https://www.pexels.com/photo/person-holding-a-blister-pack-3923159/",
        "px": (4000, 6000),
        "title": "Hands holding a strip of tablets",
        "use": "Pharmacy",
    },
    "eye_exam": {
        "asset": "PH-29", "src": "src-eye-exam.jpg", "id": 6749698,
        "creator": "Antoni Shkraba",
        "url": "https://www.pexels.com/photo/a-patient-having-eye-examination-6749698/",
        "px": (5917, 3945),
        "title": "Eye examination on a vision testing instrument",
        "use": "Eye services",
    },
    "ent_exam": {
        "asset": "PH-30", "src": "src-ent-exam2.jpg", "id": 5206951,
        "creator": "Karola G",
        "url": "https://www.pexels.com/photo/a-patient-having-ear-examination-5206951/",
        "px": (6720, 4480),
        "title": "Otoscope examination of an ear",
        "use": "ENT",
    },
    "ward": {
        "asset": "PH-31", "src": "src-ward.jpg", "id": 39128512,
        "creator": "Maxx Sas",
        "url": "https://www.pexels.com/photo/empty-hospital-room-in-accra-ghana-39128512/",
        "px": (2510, 4032),
        "title": "Inpatient beds in a hospital room",
        "use": "Inpatient care",
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
