"""Build the BCM Medical Centre set.

Same press geometry and typographic system as the CarePoint set, but:
  · identity  BCM Medical Centre, no telephone numbers supplied
  · layout    reference-literal: white logo plate top-left, photo full bleed,
              solid navy caption band at the foot
  · photos    the licensed Pexels originals, retouched with an AI image editor
              so the people reflect the community the clinic serves
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

import bcm_brand as BR
import cp_build_artwork as ART
import cp_docs as DOC
import cp_docutil as DU
import cp_mockup as MK
import cp_panels as PN
import cp_photos as P
import cp_render as R
import cp_site as SITE
import cp_spec as SPEC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "bcm")

EDITS = {
    "dental": "ph-dental.jpg",
    "paeds": "ph-paeds.jpg",
    "lab": "ph-lab.jpg",
    "physio": "ph-physio.jpg",
    "pharmacy": "ph-pharmacy.jpg",
    "reception": "ph-reception.jpg",
}

PLACEMENT = {"BM-01": "Left inner leaf · upper", "BM-04": "Left inner leaf · lower",
             "BM-02": "Right inner leaf · upper", "BM-05": "Right inner leaf · lower",
             "BM-03": "Right outer leaf · upper", "BM-06": "Right outer leaf · lower",
             "BM-07": "Left outer leaf · upper", "BM-08": "Left outer leaf · lower"}

ROLE = {"BM-01": "Dental suite", "BM-02": "Children's clinic", "BM-03": "Laboratory",
        "BM-04": "Physiotherapy", "BM-05": "Directory", "BM-06": "Pharmacy",
        "BM-07": "Antenatal", "BM-08": "Reception"}

FOCUS = {"BM-01": (0.50, 0.34), "BM-02": (0.46, 0.28), "BM-03": (0.52, 0.34),
         "BM-04": (0.48, 0.34), "BM-06": (0.62, 0.42), "BM-07": (0.50, 0.40),
         "BM-08": (0.50, 0.46)}


def configure():
    for mod in (ART, DOC, DU, MK, R, SITE, SPEC):
        mod.use_brand(BR)
    ART.OUT = os.path.join(BASE, "artwork")
    DOC.BASE = BASE
    SPEC.BASE = BASE
    SITE.BASE = BASE
    SITE.ART = os.path.join(BASE, "artwork")
    SITE.WEB = os.path.join(BASE, "web")
    MK.OUT = os.path.join(BASE, "lookbook", "mockups")
    MK.SIGN_H = 620
    P.CACHE_DIR = os.path.join(ROOT, "source", ".work", "bcm_photos")
    DOC.PLACEMENT = dict(PLACEMENT)
    SPEC.PLACEMENT = dict(PLACEMENT)
    SITE.PLACEMENT = dict(PLACEMENT)
    SITE.ROLE = dict(ROLE)


def retouch_photos():
    src_dir = os.path.join(ROOT, "assets", "photos")
    for key, fname in EDITS.items():
        path = os.path.join(src_dir, "edited", fname)
        w, h = Image.open(path).size
        m = P.PHOTOS[key]
        m["original_src"] = m["src"]
        m["src"] = os.path.join("edited", fname)
        m["px"] = (w, h)
        m["edit"] = ("Retouched with an AI image editor: skin tone of the people altered so the "
                     "panel represents the clinic's community. Scene, pose and clothing unchanged.")
        m["orig_px"] = None


def panels():
    out = []
    for p in PN.PANELS:
        q = copy.deepcopy(p)
        q["id"] = p["id"].replace("CP-", "BM-")
        if q["id"] in FOCUS:
            q["focus"] = FOCUS[q["id"]]
        q["zoom"] = 1.0
        out.append(q)
    return out


def main():
    configure()
    retouch_photos()
    plist = panels()
    PN.PANELS[:] = plist          # the document builders read this list

    os.makedirs(os.path.join(BASE, "artwork"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "docs"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "lookbook"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "web"), exist_ok=True)

    for p in PN.PANELS:
        path = os.path.join(ART.OUT, f"{p['id']}.pdf")
        ART.build(p, path)
    print("artwork", len(PN.PANELS))

    print("mockups", MK.build(False, "M-01-shopfront-day.png"))
    print("mockups", MK.build(True, "M-02-shopfront-night.png"))
    print("docs", DOC.schedule())
    print("docs", DOC.lookbook())
    print("docs", SPEC.build())
    print("combined", SITE.combined())
    print("web", len(SITE.previews()))
    print("web", len(SITE.mockup_jpgs()))
    print("html", SITE.html())


if __name__ == "__main__":
    main()
