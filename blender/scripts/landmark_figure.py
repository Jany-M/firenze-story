"""Statues as figures: a human body built from posed joints (ellipsoids for head, chest, belly, pelvis, hands and feet;
tapered limbs with rounded ends), smooth-shaded. Seen from the street or the terrace a statue reads by its silhouette and
pose – contrapposto, a raised arm, a reclining body on its elbow – which this gives at a few hundred faces, where the old
stand-ins were three boxes.

Joints are given in a figure frame in units of the standing height (H = 1): x to the figure's right, y forwards (the way it
looks), z up from the soles. `figure(part, mat, origin, forward, H, pose)` places it: origin = the point under the
pelvis at sole level, forward = horizontal direction it faces. Poses below are read from photographs of the works (credited
on each landmark's library page); proportions are the canon's (head 1/8 of the height), the details *inferred*.
"""
import math
import bmesh
from mathutils import Vector, Matrix
from landmark_kit import bm_for

def ellipsoid(bm, c, r, rot=Matrix.Identity(3), seg=12):
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2 + 1), radius=1.0,
                              matrix=Matrix.Translation(c) @ rot.to_4x4() @ Matrix.Diagonal((r[0], r[1], r[2], 1.0)))

def limb(bm, a, b, r0, r1, seg=10):
    """A tapered limb from a (radius r0) to b (r1), with a sphere at each end so joints read round."""
    d = b - a; L = d.length
    if L < 1e-6: return
    q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=seg, radius1=r0, radius2=r1, depth=L, matrix=Matrix.Translation((a + b) / 2) @ q)
    for p, r in ((a, r0), (b, r1)):
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=6, radius=r, matrix=Matrix.Translation(p))

def _rot_to(v):
    """Rotation turning +Y onto v (for an ellipsoid whose long axis is y)."""
    return Vector((0, 1, 0)).rotation_difference(v.normalized()).to_matrix()

def figure(part, mat, origin, forward, H, pose, female=False, robe=False):
    """Build a posed figure. pose: dict of joints (x right, y forward, z up, H = 1); see the presets below."""
    bm = bm_for(part, mat); bm.faces.ensure_lookup_table(); n0 = len(bm.faces)
    f = Vector((forward.x, forward.y, 0)).normalized(); r = Vector((f.y, -f.x, 0))      # the figure's right
    W = lambda p: origin + r * (p[0] * H) + f * (p[1] * H) + Vector((0, 0, p[2] * H))
    J = {k: W(v) for k, v in pose.items() if isinstance(v, tuple) and len(v) == 3}
    s = H                                                                                   # radii in units of H
    # trunk: pelvis, belly, chest along the spine (pelvis -> waist -> chest), turned with the line of the shoulders and hips
    sh = (J["l_sh"] - J["r_sh"]); hp = (J["l_hip"] - J["r_hip"])
    def trunk(c, half_w, depth, height, across, up):
        x = across.normalized(); z = up.normalized(); y = z.cross(x).normalized(); x = y.cross(z)
        M = Matrix((x, y, z)).transposed()
        ellipsoid(bm, c, (half_w, depth, height), M)
    up_low = (J["waist"] - J["pelvis"]); up_high = (J["chest"] - J["waist"])
    trunk(J["pelvis"], 0.112 * s * (1.1 if female else 1.0), 0.08 * s, 0.095 * s, hp, up_low)
    trunk(J["waist"], 0.1 * s * (0.9 if female else 1.0), 0.072 * s, 0.11 * s, (hp + sh) / 2, up_low + up_high)
    trunk(J["chest"], 0.135 * s * (0.88 if female else 1.0), 0.085 * s, 0.12 * s, sh, up_high)
    trunk((J["pelvis"] + J["chest"]) / 2, 0.11 * s * (0.95 if female else 1.0), 0.075 * s, 0.16 * s, (hp + sh) / 2, J["chest"] - J["pelvis"])   # one body, no rings
    if female:                                                                              # breasts
        x = sh.normalized(); z = up_high.normalized(); y = z.cross(x).normalized()
        for side in (-1, 1): ellipsoid(bm, J["chest"] + x * (side * 0.05 * s) + y * (0.06 * s) - z * (0.02 * s), (0.04 * s, 0.035 * s, 0.038 * s), seg=10)
    limb(bm, J["chest"] + up_high.normalized() * (0.06 * s), J["neck"], 0.05 * s, 0.04 * s)
    head_dir = J["head"] - J["neck"]
    look = Vector(pose.get("look", (0, 1, 0))); look = (r * look[0] + f * look[1] + Vector((0, 0, look[2]))).normalized()
    z = head_dir.normalized(); y = (look - z * look.dot(z)).normalized(); x = y.cross(z)
    ellipsoid(bm, J["head"], (0.054 * s, 0.064 * s, 0.072 * s), Matrix((x, y, z)).transposed())
    if pose.get("hair"): ellipsoid(bm, J["head"] + z * (0.015 * s) - y * (0.012 * s), (0.056 * s, 0.062 * s, 0.06 * s), Matrix((x, y, z)).transposed())
    # shoulders into the arms, the arms, the hands
    for side in ("r", "l"):
        limb(bm, J["chest"] + (J[side + "_sh"] - J["chest"]) * 0.55, J[side + "_sh"], 0.05 * s, 0.045 * s)
        limb(bm, J[side + "_sh"], J[side + "_el"], 0.047 * s, 0.034 * s)
        limb(bm, J[side + "_el"], J[side + "_wr"], 0.033 * s, 0.024 * s)
        hd = J[side + "_wr"] - J[side + "_el"]
        if not pose.get("detail"): ellipsoid(bm, J[side + "_wr"] + hd.normalized() * (0.035 * s), (0.022 * s, 0.045 * s, 0.012 * s), _rot_to(hd), seg=8)
        # legs: thigh, shin, foot
        hip = J[side + "_hip"] + (J["pelvis"] - J[side + "_hip"]) * 0.25
        limb(bm, hip, J[side + "_kn"], 0.074 * s * (1.05 if female else 1.0), 0.046 * s)
        limb(bm, J[side + "_kn"], J[side + "_an"], 0.045 * s, 0.028 * s)
        kd = J[side + "_an"] - J[side + "_kn"]                                          # the calf
        ellipsoid(bm, J[side + "_kn"] + kd * 0.3 - f * (0.012 * s), (0.045 * s, 0.1 * s, 0.045 * s), _rot_to(kd), seg=10)
        toe = J.get(side + "_toe", J[side + "_an"] + f * (0.11 * s))
        ellipsoid(bm, (J[side + "_an"] + toe) / 2 - Vector((0, 0, 0.01 * s)), (0.03 * s, 0.065 * s, 0.022 * s), _rot_to(toe - J[side + "_an"]), seg=8)
    if pose.get("detail"): _detail(bm, J, f, r, s, sh, hp, up_low, up_high, (x, y, z), pose, female)
    if robe:                                                                                # a drape over the hips and legs (a cone)
        limb(bm, J["waist"], (J["l_an"] + J["r_an"]) / 2 + Vector((0, 0, 0.02 * s)), 0.11 * s, 0.17 * s, seg=14)
    bm.faces.ensure_lookup_table()
    for k in range(n0, len(bm.faces)): bm.faces[k].smooth = True
    return J

def _frame(xv, zv):
    """A rotation with x along xv and z along zv (made orthogonal)."""
    x = xv.normalized(); z = (zv - x * zv.dot(x)).normalized(); y = z.cross(x)
    return Matrix((x, y, z)).transposed(), x, y, z

def _detail(bm, J, f, r, s, sh, hp, up_low, up_high, head_axes, pose, female):
    """The masses that make a body read as Michelangelo's rather than a mannequin (from photographs of the David and the
    Medici Times): deltoids, the chest's two planes, the belly's columns and the flanks over the hips, the buttocks, knees,
    the face's planes (brow, nose, cheeks, jaw, chin), ears, a cap of curls, the hands as palm, fingers and thumb, the
    sling (David). Sizes in units of H; each is placed on the trunk's own frame so it turns with the body."""
    M, X, Y, Z = _frame(-sh, up_high)                     # chest frame: X towards the figure's right, Y forward, Z up (right-handed)
    C = J["chest"]
    for sd in (-1, 1):                                    # pectorals and deltoids
        ellipsoid(bm, C + X * (sd * 0.055 * s) + Y * (0.062 * s) + Z * (0.015 * s), (0.06 * s, 0.03 * s, 0.045 * s), M, seg=10)
        shp = J["l_sh"] if sd > 0 else J["r_sh"]
        ellipsoid(bm, shp + Z * (0.005 * s) - (shp - C).normalized() * (0.005 * s), (0.05 * s, 0.05 * s, 0.055 * s), M, seg=10)
        ellipsoid(bm, C - Y * (0.05 * s) + X * (sd * 0.06 * s) + Z * (0.01 * s), (0.055 * s, 0.03 * s, 0.07 * s), M, seg=10)   # the back's blades
    Mw, Xw, Yw, Zw = _frame(-(hp + sh) / 2, up_low + up_high)
    W_ = J["waist"]
    if not female:
        for row in range(3):                              # the belly's columns, three pairs
            for sd in (-1, 1):
                ellipsoid(bm, W_ + Xw * (sd * 0.022 * s) + Yw * (0.058 * s) + Zw * ((0.035 - row * 0.032) * s), (0.019 * s, 0.01 * s, 0.015 * s), Mw, seg=8)
    for sd in (-1, 1):                                    # the flanks over the hips
        ellipsoid(bm, W_ + Xw * (sd * 0.085 * s) + Zw * (-0.045 * s) + Yw * (0.01 * s), (0.03 * s, 0.05 * s, 0.05 * s), Mw, seg=8)
    Mp, Xp, Yp, Zp = _frame(-hp, up_low)
    for sd in (-1, 1):                                    # the buttocks
        ellipsoid(bm, J["pelvis"] + Xp * (sd * 0.05 * s) - Yp * (0.055 * s) - Zp * (0.02 * s), (0.055 * s, 0.045 * s, 0.06 * s), Mp, seg=10)
    for side in ("r", "l"):                               # knee caps
        kn = J[side + "_kn"]; ellipsoid(bm, kn + f * (0.032 * s), (0.026 * s, 0.02 * s, 0.03 * s), _rot_to(f), seg=8)
    # the head: brow, nose, cheekbones, jaw and chin, ears, the curls
    hx, hy, hz = head_axes; H0 = J["head"]; Mh = Matrix((hx, hy, hz)).transposed()
    ellipsoid(bm, H0 + hy * (0.052 * s) + hz * (0.018 * s), (0.04 * s, 0.014 * s, 0.012 * s), Mh, seg=8)              # brow
    ellipsoid(bm, H0 + hy * (0.064 * s) - hz * (0.004 * s), (0.008 * s, 0.012 * s, 0.022 * s), Mh, seg=8)             # nose
    for sd in (-1, 1):
        ellipsoid(bm, H0 + hx * (sd * 0.03 * s) + hy * (0.042 * s) - hz * (0.012 * s), (0.016 * s, 0.014 * s, 0.014 * s), Mh, seg=8)   # cheeks
        ellipsoid(bm, H0 + hx * (sd * 0.054 * s) - hz * (0.004 * s), (0.006 * s, 0.014 * s, 0.02 * s), Mh, seg=6)    # ears
    ellipsoid(bm, H0 + hy * (0.036 * s) - hz * (0.05 * s), (0.032 * s, 0.026 * s, 0.022 * s), Mh, seg=8)             # jaw and chin
    if pose.get("hair"):                                  # a cap of curls over the top and the back
        for k in range(22):
            a = k * 2.399; e = 0.25 + 0.65 * ((k * 0.618) % 1.0)
            d = (hx * (math.cos(a) * math.cos(e)) + hy * (math.sin(a) * math.cos(e) * 0.9 - 0.15) + hz * math.sin(e)).normalized()
            if d.dot(hy) > 0.55 and d.dot(hz) < 0.6: continue                              # leave the face free
            ellipsoid(bm, H0 + d * (0.066 * s), (0.016 * s, 0.016 * s, 0.014 * s), _rot_to(d), seg=6)
    # hands: a palm, four fingers and a thumb, curled by pose["grip"] (0 open … 1 a fist)
    for side in ("r", "l"):
        wr, el = J[side + "_wr"], J[side + "_el"]; d = (wr - el).normalized()
        side_v = (r if side == "r" else -r); side_v = (side_v - d * side_v.dot(d)).normalized(); palm_n = d.cross(side_v)
        g = pose.get(side + "_grip", 0.5)
        c = wr + d * (0.03 * s)
        ellipsoid(bm, c, (0.024 * s, 0.032 * s, 0.011 * s), _frame(side_v, palm_n)[0] @ Matrix.Rotation(0, 3, "X"), seg=8)
        for k in range(4):
            base = c + d * (0.03 * s) + side_v * ((k - 1.5) * 0.011 * s)
            tip = base + d * (0.04 * s * (1 - 0.6 * g)) + palm_n * (0.03 * s * g)
            limb(bm, base, tip, 0.0062 * s, 0.005 * s, seg=6)
        tb = c - side_v * (0.022 * s); limb(bm, tb, tb + d * (0.025 * s) - side_v * (0.012 * s) + palm_n * (0.012 * s), 0.007 * s, 0.0055 * s, seg=6)
    if pose.get("sling"):                                 # from the left hand over the shoulder, down the back to the right hand
        pts = [J["l_wr"] + Vector((0, 0, 0.02 * s)), J["l_sh"] + Vector((0, 0, 0.05 * s)) - f * (0.02 * s),
               J["chest"] - f * (0.1 * s) + (J["l_sh"] - J["chest"]) * 0.3, J["waist"] - f * (0.1 * s) + r * (0.06 * s),
               J["r_wr"] - f * (0.03 * s)]
        for a, b in zip(pts, pts[1:]): limb(bm, a, b, 0.006 * s, 0.006 * s, seg=5)
        ellipsoid(bm, pts[2], (0.03 * s, 0.02 * s, 0.04 * s), seg=8)                    # the pouch hanging on the back

def mirror(pose):
    """The same pose with left and right exchanged (x negated)."""
    out = {}
    for k, v in pose.items():
        if not (isinstance(v, tuple) and len(v) == 3): out[k] = v; continue
        k2 = ("l" + k[1:]) if k.startswith("r_") else ("r" + k[1:]) if k.startswith("l_") else k
        out[k2] = (-v[0], v[1], v[2])
    if "look" in out: out["look"] = (-out["look"][0], out["look"][1], out["look"][2])
    return out

# ------------------------------------------------------------------ poses
# Michelangelo's David (1501–04): weight on the right leg, the left relaxed and set forward and out; the right hip up and the
# right shoulder down; the right arm hangs along the thigh (the stone in the hand), the left raised, the hand at the left
# shoulder holding the sling over it; the head turned to his left. Bronze cast by Clemente Papi, Piazzale 1873.
DAVID = {
    "pelvis": (0.0, 0.0, 0.535), "waist": (0.0, 0.005, 0.625), "chest": (-0.008, 0.0, 0.735), "neck": (-0.005, 0.0, 0.865),
    "head": (-0.012, 0.008, 0.932), "look": (-0.55, 0.85, 0.0), "hair": True, "detail": True, "sling": True, "r_grip": 0.7, "l_grip": 0.5,
    "r_sh": (0.165, -0.005, 0.805), "l_sh": (-0.17, 0.0, 0.825),
    "r_el": (0.205, -0.01, 0.635), "r_wr": (0.21, 0.015, 0.495),
    "l_el": (-0.215, 0.07, 0.72), "l_wr": (-0.115, 0.06, 0.835),
    "r_hip": (0.085, 0.0, 0.54), "r_kn": (0.075, 0.01, 0.285), "r_an": (0.065, -0.01, 0.04), "r_toe": (0.08, 0.1, 0.01),
    "l_hip": (-0.085, 0.0, 0.52), "l_kn": (-0.105, 0.07, 0.29), "l_an": (-0.125, 0.065, 0.045), "l_toe": (-0.165, 0.16, 0.01),
}
# The four Times of Day from the Medici tombs in San Lorenzo, reclining (bronze copies on the monument's pedestal): lying
# along x of their own frame. Given here in the figure frame of a body lying on its back propped on the far elbow: x along
# the body (head towards +x… expressed through the joints), y towards the viewer, z up from the bed it lies on.
# Night (a woman) lies with the head bowed on the raised right arm, the left leg drawn up; Dawn (a woman) half turned, waking,
# the near leg bent; Day (a man) turned away, the near arm behind the back, a massive shoulder raised; Dusk (a man) leaning
# back, the head lowered, the near leg crossed.
def recline(head_up=0.36, knee=0.26, arm="head", bend=0.0):
    p = {
        "pelvis": (0.0, 0.0, 0.10), "waist": (0.12, 0.0, 0.15), "chest": (0.26, 0.0, 0.22), "neck": (0.36, 0.01, head_up - 0.04),
        "head": (0.43, 0.02, head_up), "look": (0.4, 1.0, -0.2 - bend), "hair": True, "detail": True,
        "r_sh": (0.3, 0.13, 0.27), "l_sh": (0.29, -0.11, 0.21),
        "l_el": (0.22, -0.16, 0.05), "l_wr": (0.38, -0.12, 0.08),
        "r_el": (0.2, 0.21, 0.2), "r_wr": (0.08, 0.2, 0.12),
        "r_hip": (0.0, 0.08, 0.1), "r_kn": (-0.22, 0.13, knee), "r_an": (-0.42, 0.12, 0.05), "r_toe": (-0.47, 0.15, 0.02),
        "l_hip": (0.0, -0.08, 0.08), "l_kn": (-0.26, -0.06, 0.08), "l_an": (-0.52, -0.05, 0.05), "l_toe": (-0.6, -0.03, 0.04),
    }
    if arm == "head":                                       # the near arm raised, the head resting on the hand (Night)
        p["r_el"] = (0.3, 0.2, 0.42); p["r_wr"] = (0.42, 0.1, 0.39)
    elif arm == "back":                                     # the near arm drawn behind the back (Day)
        p["r_el"] = (0.18, 0.06, 0.28); p["r_wr"] = (0.08, -0.04, 0.2)
    return p

def lying(part, mat, centre, along, out, H, pose, female=False):
    """A reclining figure: `centre` under its pelvis on the bed, `along` the direction its head lies, `out` towards the
    viewer. The pose is in a frame x = along, y = out, z = up; `figure` takes x right / y forward, so it is turned here:
    the figure frame's 'right' is `along`, its 'forward' is `out`."""
    a = Vector((along.x, along.y, 0)).normalized(); o = Vector((out.x, out.y, 0)).normalized()
    if a.dot(Vector((o.y, -o.x, 0))) < 0: pose = mirror_x(pose)        # `figure`'s right is (o.y, -o.x): head the other way
    return figure(part, mat, centre, o, H, pose, female=female)

def mirror_x(pose):
    """x negated only (the body turned end for end along x, same side to the viewer)."""
    return {k: ((-v[0], v[1], v[2]) if isinstance(v, tuple) and len(v) == 3 else v) for k, v in pose.items()}
