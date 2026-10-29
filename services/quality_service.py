"""
Crop Quality Grading Service

Grades a photograph of harvested produce from what a single photo can actually
show: how much of the visible skin is discoloured, cut, sunken, mouldy or unripe,
and how even the colour of the lot is. Each defect pixel is judged against the
colour of the tissue around it and against the colour of the whole lot, and only
tissue well inside a piece is judged at all - the dark line between two touching
fruit is a shadow, not damage.

What it cannot see is reported as unmeasurable rather than guessed: weight,
diameter in millimetres, size uniformity of a pile, internal quality (sugar, dry
matter, hollow heart), residue levels and any defect hidden under the pile or in
the shade.
"""

import math
import os

from PIL import Image, ImageFilter, ImageStat

# ---------------------------------------------------------------------------
# Commercial grade profiles. The price ratios are the app's own working
# assumption about how much a Indian mandi/processor typically pays per grade;
# they are not a quote and are labelled as such wherever they are shown.
# ---------------------------------------------------------------------------

GRADE_PROFILES = {
    "A": {
        "grade": "Grade A (Premium / Export Quality)",
        "badge": "badge-success",
        "description": "On the surface this photo shows, the crop is almost free of dark, pale, cut or off-colour tissue and the colour is even across the pieces. That is the look buyers pay a premium for - but this says nothing about firmness, size in millimetres or internal quality, none of which a photograph can show.",
        "price_tag": "+20% to +30% over the modal rate (this app's assumption, not a quote)",
        "channel": "Direct supermarket chains, organic retailers, or export aggregators",
        "shelf_life": "7 - 14 days under continuous cold chain",
        "handling_tips": [
            "Handle into clean crates; the premium is lost to one bruise per piece.",
            "Pre-cool in the shade before loading and keep 8-12 C through transit.",
            "Sell to a named buyer on grade agreement instead of an open mandi lot."
        ]
    },
    "B": {
        "grade": "Grade B (Fair Average Quality - Standard Mandi)",
        "badge": "badge-primary",
        "description": "Some visible surface defects or colour drift are present but limited. This is ordinary trade-grade produce: it sells, at the modal rate, and should move quickly.",
        "price_tag": "Standard market / modal benchmark rate",
        "channel": "Wholesale APMC mandis, local city bazaars, regional retailers",
        "shelf_life": "4 - 7 days",
        "handling_tips": [
            "Sort out the few worst pieces; they are what a trader discounts the whole lot for.",
            "Pack in ventilated crates, not closed sacks, and keep out of direct sun.",
            "Sell within 48-72 hours while the measured colour is still fresh-market."
        ]
    },
    "C": {
        "grade": "Grade C (Processing / Industrial Grade)",
        "badge": "badge-warning",
        "description": "A large share of the photographed surface carries dark, sunken, cut, mouldy or unripe tissue. Not a fresh-table lot; it will be discounted heavily and will not keep.",
        "price_tag": "-30% to -40% below the fresh table rate (this app's assumption, not a quote)",
        "channel": "Food processing units (puree, canning, juicing, dehydration), or immediate local sale",
        "shelf_life": "2 - 4 days; needs immediate handling",
        "handling_tips": [
            "Cut out and compost anything with mould before it contacts the rest of the lot.",
            "Take it to a processor or picker-aggregator the same day it is graded.",
            "Do not mix with a Grade A/B lot - one cull basket moves the whole lot down."
        ]
    }
}

# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

ANALYSIS_EDGE = 320
MIN_PRODUCE_FRACTION = 0.15
MIN_PATCH_AREA = 10

# Grade bands. The report page prints these numbers rather than its own copy of
# them, so what the UI claims a grade means cannot drift from what cuts the score.
A_MIN_SCORE = 85
B_MIN_SCORE = 65

NEIGHBOURS8 = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))

# The object's colour is sampled on this grid and blurred, so every pixel is
# compared with the colour around it rather than with the photo's average.
FIELD_BLOCK = 12


def _clamp01(x):
    return 0.0 if x <= 0 else (1.0 if x >= 1 else x)


def _ramp(x, lo, hi):
    return _clamp01((x - lo) / (hi - lo))


def _ramp_down(x, lo, hi):
    return 1.0 - _ramp(x, lo, hi)


def _read_pixels(image):
    """Resize in RGB, then convert to HSV: interpolating hue across the red
    wrap-around corrupts the colours this module measures."""
    rgb = image.convert("RGB")
    w, h = rgb.size
    scale = ANALYSIS_EDGE / float(max(w, h))
    if scale < 1.0:
        w, h = max(1, int(w * scale)), max(1, int(h * scale))
        rgb = rgb.resize((w, h), Image.BILINEAR)
    raw = rgb.convert("HSV").tobytes()
    hsv = []
    for i in range(w * h):
        j = i * 3
        hsv.append((raw[j] * (360.0 / 255.0), raw[j + 1] / 255.0, raw[j + 2] / 255.0))
    return w, h, hsv


def _components(mask, w, h, start, seen):
    """8-connected flood fill; returns the pixel indices of the region."""
    stack = [start]
    seen[start] = True
    out = [start]
    while stack:
        idx = stack.pop()
        x, y = idx % w, idx // w
        for dx, dy in NEIGHBOURS8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                nidx = ny * w + nx
                if mask[nidx] and not seen[nidx]:
                    seen[nidx] = True
                    stack.append(nidx)
                    out.append(nidx)
    return out


def _all_components(mask, w, h, min_area):
    seen = [False] * (w * h)
    comps = []
    for idx in range(w * h):
        if mask[idx] and not seen[idx]:
            comp = _components(mask, w, h, idx, seen)
            if len(comp) >= min_area:
                comps.append(comp)
    return comps


def _background_model(hsv, w, h):
    """Border pixels are almost never produce: they describe the surface the
    photo was taken against (table, crate, sack, sky, soil, hand)."""
    ring = []
    for x in range(w):
        ring.append(hsv[x])
        ring.append(hsv[(h - 1) * w + x])
    for y in range(h):
        ring.append(hsv[y * w])
        ring.append(hsv[y * w + w - 1])
    hues = sorted(p[0] for p in ring)
    sats = sorted(p[1] for p in ring)
    vals = sorted(p[2] for p in ring)
    mid = len(hues) // 2
    spread = (hues[-1] - hues[0]) / 2.0
    return {
        "hue": hues[mid],
        "sat": sats[mid],
        "val": vals[mid],
        "hue_spread": min(60.0, max(18.0, spread)),
        "varied": spread > 90.0,
    }


def _neutral_surface(hue, sat, val):
    """White, grey, cream and black: too unsaturated to be any crop's skin."""
    if sat < 0.13 and val > 0.55:
        return True
    if sat < 0.30 and val > 0.90:
        return True
    return val < 0.10


def _hue_close(a, b, tol):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d) <= tol


def _produce_mask(hsv, w, h, bg):
    """Everything that is not the background surface. On a market-pile photo the
    produce fills the frame, which is the correct answer there too."""
    mask = []
    for hue, sat, val in hsv:
        if _neutral_surface(hue, sat, val):
            mask.append(False)
            continue
        near_bg = (_hue_close(hue, bg["hue"], bg["hue_spread"])
                   and abs(sat - bg["sat"]) < 0.30 and abs(val - bg["val"]) < 0.32)
        if bg["varied"]:
            near_bg = near_bg and sat < 0.45        # a colourful border is not a reliable cue
        mask.append(not near_bg)
    frac = sum(1 for m in mask if m) / float(w * h)
    return mask, frac


def _stats(comp, w, h, mask):
    n = len(comp)
    xs = [i % w for i in comp]
    ys = [i // w for i in comp]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    # Perimeter = sides of the region that touch a non-region pixel or the edge
    # of the frame. Counting only frame edges would rate every interior blob as
    # a perfect circle, which is what made the first shape gate meaningless.
    perim = 0
    for i in comp:
        x, y = i % w, i // w
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or not mask[ny * w + nx]:
                perim += 1
    cx = sum(xs) / float(n)
    cy = sum(ys) / float(n)
    mxx = sum((x - cx) ** 2 for x in xs) / float(n)
    myy = sum((y - cy) ** 2 for y in ys) / float(n)
    mxy = sum((x - cx) * (y - cy) for x, y in zip(xs, ys)) / float(n)
    tr = mxx + myy
    det = max(0.0, mxx * myy - mxy * mxy)
    disc = math.sqrt(max(0.0, tr * tr / 4.0 - det))
    major = tr / 2.0 + disc
    minor = max(1e-6, tr / 2.0 - disc)
    return {
        "area": n,
        "circularity": _clamp01(4.0 * math.pi * n / (perim * perim) if perim else 0.0),
        "elongation": min(8.0, math.sqrt(major / minor)),
        "bbox_fill": n / float(max(1, (x1 - x0 + 1) * (y1 - y0 + 1))),
        "cx": cx, "cy": cy,
        "bbox": (x0, y0, x1, y1),
    }


def _patch_summary(comps, w, h, total_area, mask):
    if not comps:
        return {"count": 0, "area_pct": 0.0, "mean_area": 0.0, "largest_pct": 0.0,
                "circularity": 0.0, "elongation": 0.0, "spread": 0.0}
    areas = [len(c) for c in comps]
    stats = [_stats(c, w, h, mask) for c in comps]
    cells = set()
    cell_of = lambda x, y: (x // 4, y // 4)          # noqa: E731 - 4x4 grid of the frame
    for s in stats:
        cells.add(cell_of(int(s["cx"]), int(s["cy"])))
    grid = max(1, (w // 4) * (h // 4))
    return {
        "count": len(comps),
        "area_pct": sum(areas) / float(total_area),
        "mean_area": sum(areas) / float(len(areas)),
        "largest_pct": max(areas) / float(total_area),
        "circularity": sum(s["circularity"] * a for s, a in zip(stats, areas)) / float(sum(areas)),
        "elongation": sum(s["elongation"] * a for s, a in zip(stats, areas)) / float(sum(areas)),
        "spread": len(cells) / float(grid),
    }


def _median(values):
    s = sorted(values)
    return s[len(s) // 2] if s else 0.0


def _enclosed(produce, w, h):
    """Non-produce pixels that the produce wraps around - a mould patch, a cut
    face, a pale bruise - belong to the object, not to the background."""
    outside = [False] * (w * h)
    stack = []
    for x in range(w):
        for idx in (x, (h - 1) * w + x):
            if not produce[idx] and not outside[idx]:
                outside[idx] = True
                stack.append(idx)
    for y in range(h):
        for idx in (y * w, y * w + w - 1):
            if not produce[idx] and not outside[idx]:
                outside[idx] = True
                stack.append(idx)
    while stack:
        idx = stack.pop()
        x, y = idx % w, idx // w
        for dx, dy in NEIGHBOURS8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                nidx = ny * w + nx
                if not produce[nidx] and not outside[nidx]:
                    outside[nidx] = True
                    stack.append(nidx)
    object_mask = [produce[i] or not outside[i] for i in range(w * h)]
    pockets = [i for i in range(w * h) if not produce[i] and not outside[i]]
    return object_mask, pockets


def _hue_dist(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _local_field(hsv, w, h, obj):
    """Colour of the object on a coarse grid, averaged over each block's 3x3
    neighbourhood. Comparing a pixel with the colour *around* it is what tells a
    shadow (broad, same hue, same saturation) from a blemish (local, off-colour).
    Hue is averaged as a vector so reds either side of 0/360 do not cancel."""
    B = FIELD_BLOCK
    gw, gh = -(-w // B), -(-h // B)
    n = gw * gh
    cos_ = [0.0] * n
    sin_ = [0.0] * n
    sat_ = [0.0] * n
    val_ = [0.0] * n
    cnt_ = [0] * n
    for i, (hu, sa, va) in enumerate(hsv):
        if not obj[i]:
            continue
        b = (i // w) // B * gw + (i % w) // B
        rad = math.radians(hu)
        cos_[b] += math.cos(rad)
        sin_[b] += math.sin(rad)
        sat_[b] += sa
        val_[b] += va
        cnt_[b] += 1
    field = []
    for by in range(gh):
        for bx in range(gw):
            c = s = sa = sv = ct = 0.0
            for dy in (-1, 0, 1):
                ny = by + dy
                if not 0 <= ny < gh:
                    continue
                for dx in (-1, 0, 1):
                    nx = bx + dx
                    if 0 <= nx < gw:
                        b = ny * gw + nx
                        c += cos_[b]
                        s += sin_[b]
                        sa += sat_[b]
                        sv += val_[b]
                        ct += cnt_[b]
            if ct <= 0:
                field.append(None)
            else:
                field.append((math.degrees(math.atan2(s, c)) % 360.0, sa / ct, sv / ct))
    return gw, gh, field


def _skin_depth(produce, w, h):
    """How far each skin pixel sits from the nearest non-skin pixel (the gap
    between two pieces, a mould colony, a cut face, the edge of the frame).
    A two-pass chamfer distance transform.

    Defects are judged on interior pixels only. The dark crevice between two
    touching apples is a boundary, not damage, and it is the same colour and
    brightness as rot - depth is the only thing that tells them apart."""
    big = float(w + h)
    d = [0.0 if not produce[i] else big for i in range(w * h)]
    for y in range(h):
        for x in range(w):
            i = y * w + x
            cur = d[i]
            if y:
                v = d[i - w] + 1.0
                if v < cur:
                    cur = v
                if x:
                    v = d[i - w - 1] + 1.42
                    if v < cur:
                        cur = v
                if x + 1 < w:
                    v = d[i - w + 1] + 1.42
                    if v < cur:
                        cur = v
            if x:
                v = d[i - 1] + 1.0
                if v < cur:
                    cur = v
            d[i] = cur
    for y in range(h - 1, -1, -1):
        for x in range(w):
            i = y * w + x
            cur = d[i]
            if y + 1 < h:
                v = d[i + w] + 1.0
                if v < cur:
                    cur = v
                if x:
                    v = d[i + w - 1] + 1.42
                    if v < cur:
                        cur = v
                if x + 1 < w:
                    v = d[i + w + 1] + 1.42
                    if v < cur:
                        cur = v
            if x + 1 < w:
                v = d[i + 1] + 1.0
                if v < cur:
                    cur = v
            d[i] = cur
    return d


def _glare(val, sat):
    """A blown specular highlight on glossy skin: pure white with no colour in
    it at all. Mould is off-white and still carries a little colour, so this is
    the line between shine, which a buyer does not discount, and rot."""
    return val > 0.93 and sat < 0.14


def _measure(hsv, w, h, produce, pockets, gw, gh, field, depth):
    """Classify the object's skin against the colour of the tissue next to it and
    against the colour of the lot as a whole. The dominant colour is taken from
    the skin only, so a white mould colony cannot redefine what 'normal' looks
    like."""
    skin = [hsv[i] for i in range(w * h) if produce[i]]
    dom_hue = _median([p[0] for p in skin])
    dom_sat = _median([p[1] for p in skin])
    dom_val = _median([p[2] for p in skin])
    dom_green = 60.0 <= dom_hue < 170.0
    fallback = (dom_hue, dom_sat, dom_val)
    pocket = set(pockets)
    n_px = w * h
    obj_px = len(skin) + len(pocket)
    interior = max(4.0, 0.03 * max(w, h))

    # Deliberately not done, because it was tried and measured worse (9/15 against
    # the by-eye grades instead of 10/15, and it caught no additional bad lot):
    # comparing each grid cell's own mean colour with the lot's dominant colour,
    # to charge the *interior* of a broad mould colony rather than only its rim,
    # since inside a colony every pixel matches its neighbourhood. On the labelled
    # set it fired on the dim, desaturated side of clean green capsicums and on
    # shadowed onion skins and called them rot, while the mouldy kiwi and the sooty
    # pomegranate it is meant to catch were unchanged - their colonies are not
    # uniform enough by hue or saturation to pass as foreign tissue at cell level.
    # Colour statistics alone do not perform object recognition; the missed broad
    # colonies are published as the measured weakness instead of being papered over.
    dark = [False] * n_px
    pale = [False] * n_px
    offcol = [False] * n_px
    green = [False] * n_px
    even = [False] * n_px
    boundary_px = 0

    for idx in range(n_px):
        hue, sat, val = hsv[idx]
        if produce[idx]:
            if 60.0 <= hue < 170.0:
                green[idx] = True
            if _hue_dist(hue, dom_hue) <= 42.0 and abs(val - dom_val) < 0.30:
                even[idx] = True
            if depth[idx] < interior:
                boundary_px += 1
                continue
            c = (idx // w) // FIELD_BLOCK * gw + (idx % w) // FIELD_BLOCK
            f_hue, f_sat, f_val = field[c] or fallback
            if val < f_val - 0.16 or val < min(0.10, dom_val - 0.32):
                dark[idx] = True
            elif val > f_val + 0.14 and sat < max(0.10, f_sat * 0.60) and not _glare(val, sat):
                pale[idx] = True
            elif _hue_dist(hue, f_hue) > 30.0 and sat > 0.22 and abs(val - f_val) < 0.22:
                offcol[idx] = True
        elif idx in pocket:
            # A hollow the crop wraps around. Pale and washed out is mould or a
            # cut face; near black is a hole or sooty rot. The grey-brown shadow
            # between two pieces of touching fruit is neither, and is not charged,
            # and neither is a blown specular highlight on glossy skin.
            if val < 0.12:
                dark[idx] = True
            elif (not _glare(val, sat) and sat < dom_sat * 0.55
                  and val > dom_val + 0.10):
                pale[idx] = True

    # Anything the crop wraps right around is not sound skin either: a mould
    # colony, a cut face, a hole or a cavity. It only reaches this set if it is
    # fully enclosed, so the shadow between two pieces of touching fruit, which
    # opens onto the table, is not charged here.
    blemish = [dark[i] or pale[i] or offcol[i] or i in pocket for i in range(n_px)]
    comps = _all_components(blemish, w, h, MIN_PATCH_AREA)
    compact, sprawl_px = [], 0
    for comp in comps:
        st = _stats(comp, w, h, blemish)
        # Thin, sprawling dark tissue is a crack or a shadow line running across
        # the frame; a rounded patch is the blemish a buyer discounts for.
        if st["elongation"] > 3.4 and st["circularity"] < 0.35:
            sprawl_px += len(comp)
        else:
            compact.append(comp)
    # Percentages are taken against the whole detected surface. Judging only the
    # skin away from the piece edges would let a photo where most of the crop is
    # edge look cleaner than it is, so the unjudged rim is reported instead.
    raw = lambda arr: sum(1 for v in arr if v) / float(obj_px)      # noqa: E731

    return {
        "dominant_hue": round(dom_hue, 1),
        "dominant_saturation": round(dom_sat, 3),
        "dominant_value": round(dom_val, 3),
        "dominant_is_green": dom_green,
        "object_px": obj_px,
        "pocket_pct": len(pocket) / float(obj_px),
        "interior_px": interior,
        "defect": _patch_summary(compact, w, h, obj_px, blemish),
        "defect_raw_pct": raw(blemish),
        "boundary_pct": boundary_px / float(obj_px),
        "sprawl_pct": sprawl_px / float(obj_px),
        "dark_pct": raw(dark),
        "pale_pct": raw(pale),
        "offcol_pct": raw(offcol),
        "green_tissue_pct": raw(green),
        # Green capsicum, cluster tomatoes and leaf crops are supposed to be
        # green, so greenness is only charged against a lot that is not itself
        # a green crop.
        "unripe_green_pct": 0.0 if dom_green else raw(green),
        "colour_even_pct": raw(even),
    }


def _photo_quality(image):
    small = image.convert("L").resize((240, 240))
    edges = small.filter(ImageFilter.FIND_EDGES)
    sharpness = ImageStat.Stat(edges).mean[0]
    brightness = ImageStat.Stat(small).mean[0]
    warnings = []
    if sharpness < 6.0:
        warnings.append("out of focus - edges and shallow blemishes are not resolvable")
    if brightness < 45:
        warnings.append("under-exposed - dark defects cannot be told from shadow")
    elif brightness > 225:
        warnings.append("over-exposed - washed-out skin hides discoloration")
    return {"sharpness": round(sharpness, 1), "brightness": round(brightness, 1),
            "warnings": warnings}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score(m, quality):
    """Each sub-score is 0..1 and is stated in the payload, so a user can see
    exactly which measurement moved the grade. Weight, in order: visible surface
    damage, then ripeness/colour, then how even the lot looks."""
    # Only the *area* of damaged skin is scored. The patch count is reported as
    # evidence but not charged for: on a 320 px analysis a clean load of apples
    # still resolves into two dozen one-pixel marks along the seams between
    # pieces, so a count penalty punishes a busy photo rather than a damaged one.
    clean = _ramp_down(m["defect"]["area_pct"], 0.02, 0.18)
    # Dull colour and green patches cost ripeness points, but only as far as they
    # can: a bunch of bananas with green tips is still ordinary trade grade.
    ripeness = _ramp_down(m["unripe_green_pct"], 0.08, 0.40) * (
        _ramp(m["dominant_saturation"], 0.22, 0.62))
    evenness = _ramp(m["colour_even_pct"], 0.40, 0.90)
    weights = {"clean": 0.46, "ripeness": 0.30, "evenness": 0.24}
    parts = {"clean": clean, "ripeness": ripeness, "evenness": evenness}
    score = 100.0 * sum(weights[k] * parts[k] for k in weights)
    if quality["warnings"]:
        score *= 0.92
    return round(max(5.0, min(98.0, score)), 1), parts, weights


def _grade_for(score):
    if score >= A_MIN_SCORE:
        return "A"
    if score >= B_MIN_SCORE:
        return "B"
    return "C"


def _evidence(m, produce_frac):
    ev = [f"Produce covers {round(produce_frac * 100)}% of the frame; measurements below are "
          f"percentages of that area, not of the whole photo."]
    ev.append(f"Dominant skin colour measured at hue {m['dominant_hue']} degrees, "
              f"saturation {m['dominant_saturation']}, brightness {m['dominant_value']}"
              + (" - the lot is a green crop, so greenness is not held against it."
                 if m["dominant_is_green"] else "."))
    ev.append(f"Rounded surface blemishes (darker, paler or a different colour than the tissue "
              f"around them): {m['defect']['count']} patches covering "
              f"{round(m['defect']['area_pct'] * 100, 1)}% of the measured surface"
              + (f", the largest {round(m['defect']['largest_pct'] * 100, 1)}% of it."
                 if m["defect"]["count"] else "."))
    ev.append(f"Tissue not judged at all: {round(m['boundary_pct'] * 100, 1)}% of the skin lies "
              "within a few pixels of the edge between two pieces, where a shadow and a bruise "
              "look identical; thin sprawling dark tissue (another "
              f"{round(m['sprawl_pct'] * 100, 1)}%) is treated as the gap between pieces rather "
              "than as damage.")
    ev.append(f"Split by kind: darker than the tissue around it {round(m['dark_pct'] * 100, 1)}%, "
              f"pale or bleached {round(m['pale_pct'] * 100, 1)}%, a different hue than its "
              f"neighbourhood {round(m['offcol_pct'] * 100, 1)}%, tissue enclosed by the crop "
              f"(mould, a cut face, a hole) {round(m['pocket_pct'] * 100, 1)}%.")
    ev.append(f"Unripe or leafy green on a non-green crop: {round(m['unripe_green_pct'] * 100, 1)}%.")
    ev.append(f"{round(m['colour_even_pct'] * 100, 1)}% of the surface sits within 42 degrees hue and "
              "0.30 brightness of the dominant colour, which is what 'even colour' means here.")
    ev.append("Size and shape uniformity could not be measured: pieces that touch each other merge "
              "into one region, and a photograph carries no scale, so no diameter in millimetres "
              "is claimed.")
    return ev


UNMEASURABLE = [
    "Weight, diameter in millimetres and count per box - a photo has no scale in it.",
    "Size and shape uniformity of the lot - pieces that touch merge into one region, so they "
    "cannot be counted or compared reliably from one frame.",
    "Firmness, sugar, acidity and internal defects such as hollow heart or borer damage.",
    "Pesticide residue, moisture content and anything a buyer checks by hand or in a lab.",
    "Defects on the faces hidden by the pile, by shading or by the angle of this one photo, and "
    "anything in the rim of tissue where two pieces meet.",
]

# Measured, not assumed. Fifteen produce photographs were graded by eye from the
# contact sheet before the tool saw them, then graded by this module
# (scratch/eval_quality.py holds the set and the run). Read per *printed* grade:
# of the photos this module printed Grade A on, 2 of 3 were A by eye. The other
# reading, agreement with the person's grade, is A 2/3, B 6/7, C 2/5 and 10/15
# overall; both are printed by the harness.
GRADE_AGREEMENT = {"A": (2, 3), "B": (6, 8), "C": (2, 3)}
TESTED_PHOTOS = 15
TESTED_MATCHED = 10
# The direction that matters commercially: photos a person called Grade C. Two
# printed C, two printed A or B, and one was refused outright rather than given a
# grade, so it was not passed as clean either.
CATCH_C_TRUE = 5
CATCH_C_FOUND = 2
CATCH_C_REFUSED = 1
# Ten photographs of things that are not a harvested crop (book plates, an
# engraving, a sandwich, a fruit fly, a logo, a machine, a wall, chips on a
# plate, a wide market scene). The tool was asked to refuse them.
NON_PRODUCE_TESTED = 10
NON_PRODUCE_REFUSED = 4


def _agreement(grade):
    ok, n = GRADE_AGREEMENT.get(grade, (0, 0))
    return ok, n


def assess_crop_quality(image_path, crop_name="Produce"):
    """Grade a produce photo from measured pixels, or refuse when it holds none."""
    if not os.path.exists(image_path):
        return {"success": False, "error": "Image file not found on the server."}
    try:
        with Image.open(image_path) as img:
            img.load()
            w, h, hsv = _read_pixels(img)
            quality = _photo_quality(img)
    except Exception as exc:
        return {"success": False, "error": f"Failed to read image: {exc}"}

    bg = _background_model(hsv, w, h)
    produce, frac = _produce_mask(hsv, w, h, bg)
    if frac < MIN_PRODUCE_FRACTION:
        return {
            "success": False,
            "error": ("Too little of this frame is produce to grade. Lay the harvest out on a plain "
                      "surface and fill the frame with the pieces."),
        }
    if frac > 0.97:
        return {
            "success": False,
            "error": ("This photo is one unbroken colour field, so there is no surface to measure "
                      "defects against. Move back so individual pieces and their edges are visible."),
        }

    # Patches the produce wraps around (mould, a cut face, a pale bruise) belong to
    # the object, so the measurement runs on produce + pockets, not on skin alone.
    # Piece geometry is deliberately not used to decide whether a photo is produce
    # at all: on a pile of touching fruit every region merges into one sprawling
    # blob whose outline is as jagged as a brick wall's, so no shape test tells the
    # two apart reliably enough to refuse a farmer's photo over.
    object_mask, pockets = _enclosed(produce, w, h)

    gw, gh, field = _local_field(hsv, w, h, produce)
    depth = _skin_depth(produce, w, h)
    m = _measure(hsv, w, h, produce, pockets, gw, gh, field, depth)

    if m["dominant_saturation"] < 0.12:
        return {
            "success": False,
            "error": ("The detected surface carries almost no colour (median saturation "
                      f"{m['dominant_saturation']}), which reads as paper, print or a grey scene "
                      "rather than produce. Photograph the actual harvest."),
        }
    if m["green_tissue_pct"] > 0.65:
        return {
            "success": False,
            "error": ("Two thirds of what was detected is green leaf and stem tissue, which reads as "
                      "foliage or a standing crop rather than a picked lot. This tool grades the "
                      "surface of fruit, tubers and roots - photograph those."),
        }

    score, parts, weights = _score(m, quality)
    grade_key = _grade_for(score)
    profile = GRADE_PROFILES[grade_key]
    ok, n = _agreement(grade_key)

    return {
        "success": True,
        "crop_name": crop_name,
        "grade": grade_key,
        "grade_title": profile["grade"],
        "badge": profile["badge"],
        "description": profile["description"],
        "price_tag": profile["price_tag"],
        "recommended_channel": profile["channel"],
        "shelf_life": profile["shelf_life"],
        "handling_tips": profile["handling_tips"],
        "overall_score": score,
        "sub_scores": {k: (round(v * 100, 1) if v is not None else None) for k, v in parts.items()},
        "sub_weights": weights,
        "metrics": {
            "surface_purity_pct": round(100 - m["defect"]["area_pct"] * 100, 1),
            "dominant_saturation_pct": round(m["dominant_saturation"] * 100, 1),
            "colour_evenness_pct": round(m["colour_even_pct"] * 100, 1),
            "blemish_area_pct": round(m["defect"]["area_pct"] * 100, 1),
            "blemish_patch_count": m["defect"]["count"],
            "sprawling_tissue_pct": round(m["sprawl_pct"] * 100, 1),
            "pale_or_mould_pct": round(m["pale_pct"] * 100, 1),
            "off_hue_pct": round(m["offcol_pct"] * 100, 1),
            "unripe_green_pct": round(m["unripe_green_pct"] * 100, 1),
            "green_tissue_pct": round(m["green_tissue_pct"] * 100, 1),
            "rim_not_judged_pct": round(m["boundary_pct"] * 100, 1),
            "produce_in_frame_pct": round(frac * 100, 1),
        },
        "evidence": _evidence(m, frac),
        "unmeasurable": UNMEASURABLE,
        "image_quality": quality,
        "agreement": {"grade": grade_key, "matched_human": ok, "tested": n,
                      "overall": f"{TESTED_MATCHED}/{TESTED_PHOTOS}",
                      "catch_c": f"{CATCH_C_FOUND}/{CATCH_C_TRUE}"},
        "accuracy_note": (
            f"Grade {grade_key} is what the measured surface of this photo scored {score}/100. "
            f"On the 15 produce photographs this module was checked "
            f"against, it matched a person's grade on {TESTED_MATCHED} of {TESTED_PHOTOS}; of the "
            f"photos it printed {grade_key}, {ok} of {n} were that grade by eye. Its weakest point is "
            f"catching bad fruit: of the {CATCH_C_TRUE} lots graded C by a person it flagged "
            f"{CATCH_C_FOUND} (a further {CATCH_C_REFUSED} it refused to grade at all), so a Grade A "
            f"or B here is not proof that the hidden faces are clean. "
            "It refused "
            f"{NON_PRODUCE_REFUSED} of {NON_PRODUCE_TESTED} photographs of things that are not a "
            "harvested crop. The price ratios are this app's working assumption, not a mandi quote, "
            "and nothing here replaces a physical check of firmness, size and internal quality."
        ),
        "method": "Background separation and per-pixel colour measurement on the uploaded photo",
        "crop_note": ("The crop name you typed is only a label on the report; it does not change the "
                      "measurement, because the tool compares each piece of skin against the dominant "
                      "colour in the same photo."),
        "measurements": m,
    }
