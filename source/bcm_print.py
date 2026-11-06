"""BCM Medical Centre — one print PDF per piece.

Everything in the set broken out into single, self-contained print files, in a
numbered folder that a printer can work straight down:

    bcm/print/01-D1-P1-HIV-CARE-900x500.pdf   …   bcm/print/30-B3-COMPACT-2400x1000.pdf

Nothing is re-drawn: the pane PDFs, the banner PDFs and the sign faces are the
same files that are proved elsewhere in the set. The sign post, which was one
file holding both faces, is also split here into a file per face.

Also builds `PRINT-INDEX.pdf` and `print-manifest.csv`: the job list, so a
printer knows how many pieces to expect before they start.
"""
import csv
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib.units import mm as MM

import bcm_brand as B
import cp_docutil as D
import bcm_doors as DOORS
import bcm_sign as SIGN
import bcm_banners as BAN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SET = os.path.join(ROOT, "bcm")
OUT = os.path.join(SET, "print")
REV = "Rev A  ·  2026-11-02"

B.register_fonts()
D.use_brand(B)


def slug_service(name):
    return (name.upper().replace(" & ", "-AND-").replace(" ", "-")
            .replace("/", "-"))


def place(src, dest_name):
    """Hardlink where the filesystem allows it — one file on disk, two names."""
    dest = os.path.join(OUT, dest_name)
    if os.path.exists(dest):
        os.remove(dest)
    try:
        os.link(src, dest)
    except OSError:
        shutil.copy2(src, dest)
    return dest


def sign_tag():
    """'1219x610' — the sign's finished size, for the print file names."""
    return f"{SIGN.W:.0f}x{SIGN.H:.0f}"


def sign_faces():
    """Split the sign post into a file per face, and add option B."""
    os.makedirs(SIGN.WORK, exist_ok=True)
    made = []
    for label, fname in (("FACE A", "SIGN-A-FACE-A"), ("FACE B", "SIGN-A-FACE-B")):
        tmp = os.path.join(SIGN.WORK, f"sign_{label.replace(' ', '_').lower()}.pdf")
        SIGN.artwork(tmp, variant="A", faces=(label,))
        made.append((place(tmp, f"{fname}-{sign_tag()}.pdf"), fname))
    tmp = os.path.join(SIGN.WORK, "sign_b_face_a.pdf")
    SIGN.artwork(tmp, variant="B", faces=("FACE A",))
    made.append((place(tmp, f"SIGN-B-FACE-A-{sign_tag()}.pdf"), "SIGN-B-FACE-A"))
    return made


def pieces_list():
    """The job list, computed without touching the disk — used by the master proof."""
    pieces = []
    n = 0
    for door in DOORS.DOORS:
        prefix = door["prefix"]
        for i, (service, w, photo, pos) in enumerate(door["spec"], start=1):
            n += 1
            pieces.append((n, f"{prefix}-P{i}", service, f"{prefix}-P{i}",
                           door["folder"], "Door film", f"900 × {w} mm",
                           f"{n:02d}-{prefix}-P{i}-{slug_service(service)}-900x{w}.pdf"))
    for job in ("SIGN-A-FACE-A", "SIGN-A-FACE-B", "SIGN-B-FACE-A"):
        n += 1
        pieces.append((n, job, "Sign post panel", job, "sign", "Sign post",
                       f"{SIGN.W:.1f} × {SIGN.H:.1f} mm",
                       f"{n:02d}-{job}-{sign_tag()}.pdf"))
    for b in BAN.BANNERS:
        n += 1
        label = {1: "ROAD", 2: "SERVICES", 3: "COMPACT"}[int(b["id"].split("-")[1])]
        pieces.append((n, b["id"], b["title"], b["id"], "banners", "Banner",
                       f"{b['w']:.0f} × {b['h']:.0f} mm",
                       f"{n:02d}-{b['id'].replace('-', '')}-{label}-"
                       f"{b['w']:.0f}x{b['h']:.0f}.pdf"))
    return pieces


def build():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".pdf") or f.endswith(".csv"):
            os.remove(os.path.join(OUT, f))

    pieces = pieces_list()

    # ---- the door panes: one file each, already one pane per PDF
    for n, job, title, ref, folder, kind, size, name in pieces:
        if kind == "Door film":
            src = os.path.join(SET, folder, "artwork", f"{ref}.pdf")
            place(src, name)

    # ---- the sign post: split into a file per face
    os.makedirs(SIGN.WORK, exist_ok=True)
    for n, job, title, ref, folder, kind, size, name in pieces:
        if kind != "Sign post":
            continue
        variant, face = ref.split("-F")
        label = f"FACE {face[-1]}"
        tmp = os.path.join(SIGN.WORK, f"{ref}.pdf")
        SIGN.artwork(tmp, variant=variant[-1], faces=(label,))
        place(tmp, name)

    # ---- the banners: one file each
    for n, job, title, ref, folder, kind, size, name in pieces:
        if kind == "Banner":
            src = os.path.join(SET, "banners", "artwork", f"BCM-Banner-{ref}.pdf")
            place(src, name)

    return pieces


def index_pdf(path, pieces):
    c = D.new_doc(path, "BCM Medical Centre — print index",
                  subject="One print PDF per piece")
    D.page_bg(c, "PRINT INDEX", f"{REV}", 1,
              eyebrow="BCM  ·  MEDICAL CENTRE  ·  ONE FILE PER PIECE")

    y = D.h1(c, D.PH - 34 * MM, f"{len(pieces)} pieces, {len(pieces)} print files", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "Every piece in the set is supplied as its own print-ready PDF in this "
           "folder, numbered in the order a job should be run. All files are 1 : 1 in "
           "millimetres with bleed, crop marks and a slug strip — plot at 100 %, never "
           "scale. The multi-page proof PDFs elsewhere in the set are for approval; "
           "these are the files to send to the printer.",
           (D.PW - 2 * D.M) / MM * 0.78, 3.2, B.NAVY_MID)

    rows = []
    for n, job, title, ref, folder, kind, size, name in pieces:
        rows.append([f"{n:02d}", job, title, kind, size, name])

    cols = [("#", 10, "left"), ("Job", 18, "left"), ("Piece", 62, "left"),
            ("Type", 22, "left"), ("Finished size", 32, "left"),
            ("File", 110, "left")]
    # the set grew past one sheet, so the table breaks over as many pages as it
    # needs — 30 rows to a page, header repeated
    step = 30
    for i in range(0, len(rows), step):
        if i:
            c.showPage()
            D.page_bg(c, "PRINT INDEX", f"{REV}", 1 + i // step,
                      eyebrow="BCM  ·  MEDICAL CENTRE  ·  ONE FILE PER PIECE")
        D.table(c, D.M, (D.PH - 42 * MM) if i else 158 * MM, cols,
                rows[i:i + step], row_h=4.05 * MM, head_h=6.0 * MM, cap=2.9,
                head_cap=2.6)

    B.caps(c, D.M, 18 * MM,
           f"TOTAL {len(pieces)} FILES  ·  32 DOOR PANES OF FILM  ·  3 SIGN FACES  ·  "
           "3 BANNERS. SIGN FACES: A IS THE PRINT FILE, B IS THE SAME PANEL'S SECOND "
           "FACE — PRINT ONE PER SIDE OF THE BOARD.",
           2.6, B.GREY, "Inter-500", 0.4)
    c.save()
    return path


def manifest(path, pieces):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["job", "piece", "title", "type", "finished_mm", "file"])
        for n, job, title, ref, folder, kind, size, name in pieces:
            w.writerow([f"{n:02d}", job, title, kind, size, name])
    return path


def bundle(path, pieces):
    """All 30 pieces in one PDF, in job order — to open and check, not to plot.

    Each page keeps its own finished size and trim box, so printing this file
    page-for-page gives the same 30 sheets as the single files. The single
    files stay the deliverable; this is the one attachment a printer can flick
    through without unzipping anything.
    """
    from pypdf import PdfWriter, PdfReader

    w = PdfWriter()
    for n, job, title, ref, folder, kind, size, name in pieces:
        src = os.path.join(OUT, name)
        if not os.path.exists(src):
            continue
        r = PdfReader(src)
        for pg in r.pages:
            w.add_page(pg)
    w.add_metadata({"/Title": "BCM Medical Centre — all print files, one per page",
                    "/Author": "BCM Medical Centre — one-way vision film project",
                    "/Subject": "30 pieces, 1 : 1 in millimetres, plot at 100 %"})
    with open(path, "wb") as fh:
        w.write(fh)
    return path


def main():
    pieces = build()
    print("print files:", len(pieces))

    index_pdf(os.path.join(OUT, "PRINT-INDEX.pdf"), pieces)
    manifest(os.path.join(OUT, "print-manifest.csv"), pieces)
    bundle(os.path.join(OUT, "BCM-Print-Files-ALL.pdf"), pieces)
    print("index + manifest + one combined file")

    # REPORT.md, so the folder explains itself when it is unzipped alone
    lines = ["# BCM Medical Centre — print files", "",
             f"{len(pieces)} pieces, one print PDF each. All 1 : 1 in millimetres with "
             "bleed, crop marks and a slug strip. Plot at 100 %, never scale.", "",
             "| # | Job | Piece | Type | Finished size | File |",
             "| --- | --- | --- | --- | --- | --- |"]
    for n, job, title, ref, folder, kind, size, name in pieces:
        lines.append(f"| {n:02d} | {job} | {title} | {kind} | {size} | "
                     f"`{name}` |")
    lines += ["", "## Suppliers", ""]
    for kind, who in (("Door film", "One-way vision printer — print one file per pane, "
                                    "cut to the finished size in the name"),
                      ("Sign post", "Signwriter — print one file per face of the board"),
                      ("Banner", "Banner printer — one file per banner")):
        sel = [p for p in pieces if p[5] == kind]
        lines += [f"### {who}", "", f"{len(sel)} files:", ""]
        lines += [f"- `{p[7]}`" for p in sel]
        lines += [""]

    lines += ["## Print files zip", "",
              "`BCM-Print-Files.zip` holds exactly this folder — the 30 single print "
              "files, the index and `BCM-Print-Files-ALL.pdf`, nothing else.", "",
              "`BCM-Print-Files-ALL.pdf` is all 30 pieces in one document, one piece per "
              "page, in job order — for checking or for a printer who would rather have a "
              "single attachment. Every page keeps its own finished size, so it plots the "
              "same as the single files; the single files are still what to send.", ""]
    lines += ["## Notes", "",
              "The sign post is supplied as three files: face A and face B of the "
              "recommended option A lockup, and face A of the same panel in the option B "
              "lockup. Print one file per side of the board.",
              "",
              "The multi-page proofs elsewhere in the set are for approval only — these "
              "single files are the ones to send to a printer.",
              "",
              "Rebuild: `cd source && python3 bcm_print.py`."]
    open(os.path.join(OUT, "REPORT.md"), "w").write("\n".join(lines) + "\n")
    print("REPORT.md")

    import zipfile
    zpath = os.path.join(OUT, "BCM-Print-Files.zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".pdf") or f in ("print-manifest.csv", "REPORT.md"):
                z.write(os.path.join(OUT, f), os.path.join("BCM-Print-Files", f))
    print("zip:", f"{os.path.getsize(zpath) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
