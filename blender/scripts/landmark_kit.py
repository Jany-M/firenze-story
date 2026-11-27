"""Shared kit for the landmark models (build_duomo.py, build_campanile.py, build_baptistery.py, …).

Geometry is accumulated per (part, material) and exported as one node per pair; part names carry their dates:
"<part>@<from>-<to>". Walls are slabs with the decoration drawn on their face (panels, frames, windows) – real
geometry, a few centimetres proud, so the polychrome revetment reads at any distance. `two_phase()` builds a part twice:
bare brick core first, marble revetment later (cladding lagged the structure on most Florentine monuments).
"""
import bpy, bmesh, math, os, json
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
TEX = os.path.join(ROOT, "web", "public", "textures")
OUT = os.path.join(ROOT, "web", "public", "models", "landmarks"); os.makedirs(OUT, exist_ok=True)
NOW = 99999
T22 = math.tan(math.pi / 8)

def reset():
    """Empty Blender scene, fresh materials and geometry buffers (call once at the top of each build script)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    BMS.clear(); MATDEF.clear(); MAT.clear(); MAT.update(make_materials())

# ------------------------------------------------------------------ materials (exported to <name>_materials.json)
MATDEF = {}
def material(name, tex=None, color=(0.8, 0.8, 0.8), rough=0.6, scale=1.0, metal=0.0, tint=(1, 1, 1)):
    MATDEF["fs_" + name] = {"tex": tex, "color": list(color), "tint": list(tint), "rough": rough, "scale": scale, "metal": metal}
    m = bpy.data.materials.new("fs_" + name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if tex and os.path.exists(os.path.join(TEX, tex + "_col.jpg")):
        nt = m.node_tree; co = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (scale, scale, scale); nt.links.new(co.outputs["Object"], mp.inputs["Vector"])
        im = nt.nodes.new("ShaderNodeTexImage"); im.image = bpy.data.images.load(os.path.join(TEX, tex + "_col.jpg"), check_existing=True)
        im.projection = "BOX"; im.projection_blend = 0.2; nt.links.new(mp.outputs["Vector"], im.inputs["Vector"])
        nt.links.new(im.outputs["Color"], b.inputs["Base Color"])
    return m
def make_materials():
    return {
        "white": material("marble_white", "marble_white", (0.9, 0.89, 0.86), 0.45, 0.35),
        "green": material("marble_green", "marble_green", (0.13, 0.2, 0.16), 0.4, 0.5),
        "red":   material("marble_red", "marble_red", (0.68, 0.36, 0.32), 0.45, 0.5),
        "tile":  material("dome_tiles", "coppi", (0.66, 0.36, 0.24), 0.75, 0.55, tint=(1.0, 0.93, 0.88)),
        "roof":  material("roof_tiles", "coppi", (0.62, 0.34, 0.24), 0.8, 0.45),
        "glass": material("window_glass", None, (0.08, 0.09, 0.11), 0.15),
        "bronze":material("bronze", None, (0.35, 0.25, 0.13), 0.35, metal=0.9),
        "gold":  material("gilt_copper", None, (0.86, 0.66, 0.28), 0.25, metal=1.0),
        "brick": material("brick_masonry", "cotto", (0.56, 0.38, 0.28), 0.9, 0.6, tint=(0.92, 0.86, 0.8)),
        "dark":  material("shadow_recess", None, (0.05, 0.05, 0.05), 0.9),
        "mosaic":material("lunette_mosaic", None, (0.75, 0.6, 0.3), 0.3, metal=0.6),
        "wood":  material("door_wood", "wood", (0.32, 0.22, 0.14), 0.8, 0.8),
        "lead":  material("lead_sheet", None, (0.42, 0.44, 0.46), 0.6, metal=0.3),
    }
MAT = {}

# ------------------------------------------------------------------ geometry accumulation: one bmesh per (part, material)
BMS = {}
BARE = False            # True while generating the "before the marble" phase of a part: revetment becomes brick, panels are skipped
def bm_for(part, mat):
    if BARE and mat in ("white", "green", "red", "mosaic"): mat = "brick"
    k = (part, mat)
    if k not in BMS: BMS[k] = bmesh.new()
    return BMS[k]

def poly(bm, pts):
    vs = [bm.verts.new(p) for p in pts]
    try: bm.faces.new(vs)
    except ValueError: pass

def quad_strip(bm, A, B):
    """Faces between two equal-length point rows."""
    va = [bm.verts.new(p) for p in A]; vb = [bm.verts.new(p) for p in B]
    for i in range(len(A) - 1): bm.faces.new((va[i], va[i + 1], vb[i + 1], vb[i]))

class Frame:
    """Local frame on a wall: u along the wall, v up, n outward. p(u, v, n) -> world."""
    def __init__(s, o, u, n): s.o = Vector(o); s.u = Vector(u).normalized(); s.n = Vector(n).normalized(); s.v = Vector((0, 0, 1))
    def p(s, u, v, n=0.0): return s.o + s.u * u + s.v * v + s.n * n

def box(bm, F, u0, u1, v0, v1, n0, n1, back=True):
    """Box in frame F. back=False leaves out the n0 face: for pieces laid on a wall face (n0 = 0), whose back face would
    sit exactly on the wall and flicker against it (z-fighting, worst with double-sided materials)."""
    c = [F.p(u, v, n) for n in (n0, n1) for v in (v0, v1) for u in (u0, u1)]
    vs = [bm.verts.new(x) for x in c]
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        if f == (0, 1, 3, 2) and not back: continue
        bm.faces.new([vs[i] for i in f])
def pbox(bm, F, u0, u1, v0, v1, n0, n1):
    """Proud box on a wall face: no back face when it starts on the face (n0 == 0)."""
    box(bm, F, u0, u1, v0, v1, n0, n1, back=(n0 != 0))

def wbox(bm, x0, x1, y0, y1, z0, z1):
    box(bm, Frame((0, 0, 0), (1, 0, 0), (0, 1, 0)), x0, x1, z0, z1, y0, y1)

def arch_pts(F, u0, u1, v0, vtop, n, pointed=True, seg=10):
    """Outline (u, v) of an opening: jambs up to the springing, then a pointed (Gothic) or round arch."""
    w = u1 - u0; r = w * (0.85 if pointed else 0.5); spring = vtop - (math.sqrt(r * r - (r - w / 2) ** 2) if pointed else w / 2)
    pts = [(u0, v0), (u1, v0), (u1, spring)]
    if pointed:                                  # two arcs of radius r, centres on the springing line
        ang_apex = math.acos(((u0 + w / 2) - (u1 - r)) / r)
        for i in range(1, seg + 1):
            a = ang_apex * i / seg; pts.append((u1 - r + r * math.cos(a), spring + r * math.sin(a)))
        for i in range(seg - 1, -1, -1):
            a = ang_apex * i / seg; pts.append((u0 + r - r * math.cos(a), spring + r * math.sin(a)))
    else:
        for i in range(1, seg):
            a = math.pi * i / seg; pts.append((u0 + w / 2 + w / 2 * math.cos(a), spring + w / 2 * math.sin(a)))
        pts.append((u0, spring))
    return [F.p(u, v, n) for u, v in pts]

def opening(part, F, u0, u1, v0, vtop, depth=0.35, frame=0.45, pointed=True, fill="glass", frame_mat="white", mullion=False, lift=0.0):
    """Window/portal: frame (proud ring), dark recessed fill, optional central mullion (bifora).
    lift: extra distance off the wall, for an opening drawn inside another one's fill (a window in a blind arch), which
    would otherwise lie in the same plane and flicker against it."""
    out = arch_pts(F, u0 - frame, u1 + frame, v0 - frame * 0.3, vtop + frame, 0.08 + lift, pointed)
    inn = arch_pts(F, u0, u1, v0, vtop, 0.08 + lift, pointed)
    bm = bm_for(part, frame_mat)
    va = [bm.verts.new(p) for p in out]; vb = [bm.verts.new(p) for p in inn]
    for i in range(len(out)):
        j = (i + 1) % len(out); bm.faces.new((va[i], va[j], vb[j], vb[i]))
    # walls are solid slabs, so the opening is drawn on the face: dark fill just proud of the wall, frame prouder still
    poly(bm_for(part, fill), arch_pts(F, u0, u1, v0, vtop, 0.05 + lift, pointed))
    if mullion:
        m = (u0 + u1) / 2; pbox(bm_for(part, "white"), F, m - 0.12, m + 0.12, v0, vtop - (u1 - u0) * 0.45, 0.0, 0.1)
        # tracery: small oculus above the two lights
        poly(bm_for(part, "white"), [F.p(m + 0.5 * math.cos(a), vtop - (u1 - u0) * 0.3 + 0.5 * math.sin(a), 0.07) for a in [i / 12 * 2 * math.pi for i in range(12)]])

def panels(part, F, u0, u1, v0, v1, cols, rows, strip=0.24, proud=0.04, inner="white", accent=None):
    """Florentine marble revetment: green frames around white (or red) panels, slightly proud of the wall."""
    if BARE: return
    du, dv = (u1 - u0) / cols, (v1 - v0) / rows
    g = bm_for(part, "green")
    for i in range(cols + 1):
        u = u0 + i * du; pbox(g, F, u - strip / 2, u + strip / 2, v0, v1, 0, proud)
    for j in range(rows + 1):
        v = v0 + j * dv; pbox(g, F, u0, u1, v - strip / 2, v + strip / 2, 0, proud)
    for i in range(cols):
        for j in range(rows):
            if accent and accent(i, j):          # inner red panel with its own green frame
                a = u0 + i * du + du * 0.22; b = u0 + (i + 1) * du - du * 0.22; c = v0 + j * dv + dv * 0.22; d = v0 + (j + 1) * dv - dv * 0.22
                pbox(bm_for(part, "red"), F, a, b, c, d, 0, proud * 0.6)
                for (x0, x1, y0, y1) in ((a - 0.12, a + 0.02, c - 0.12, d + 0.12), (b - 0.02, b + 0.12, c - 0.12, d + 0.12), (a, b, c - 0.12, c + 0.02), (a, b, d - 0.02, d + 0.12)):   # overlapping the red: no shared side faces
                    pbox(g, F, x0, x1, y0, y1, 0, proud)

def wall(part, F, u0, u1, v0, v1, thick=1.2, mat="white"):
    box(bm_for(part, mat), F, u0, u1, v0, v1, -thick, 0)

def cornice(part, F, u0, u1, v, h=0.9, proj=0.7, mat="white", arches=True):
    pbox(bm_for(part, mat), F, u0, u1, v, v + h * 0.45, 0, proj)                  # moulding
    pbox(bm_for(part, "green"), F, u0, u1, v + h * 0.45, v + h * 0.6, 0, proj * 0.8)
    pbox(bm_for(part, mat), F, u0, u1, v + h * 0.6, v + h, 0, proj * 1.1)
    if arches:                                                                    # archetti pensili below the cornice
        n = max(1, int((u1 - u0) / 1.1))
        for i in range(n):
            u = u0 + (i + 0.5) * (u1 - u0) / n; pbox(bm_for(part, mat), F, u - 0.08, u + 0.08, v - 0.9, v, 0, 0.35)

def pilaster(part, F, u, v0, v1, w=1.6, proj=0.55, stripes=True):
    pbox(bm_for(part, "white"), F, u - w / 2, u + w / 2, v0, v1, 0, proj)
    if stripes:
        pbox(bm_for(part, "green"), F, u - w / 2 - 0.02, u - w / 2 + 0.22, v0, v1, 0, proj + 0.02)
        pbox(bm_for(part, "green"), F, u + w / 2 - 0.22, u + w / 2 + 0.02, v0, v1, 0, proj + 0.02)

def pinnacle(part, c, base, h, w=1.4, mat="white"):
    x, y = c; bm = bm_for(part, mat)
    wbox(bm, x - w / 2, x + w / 2, y - w / 2, y + w / 2, base, base + h * 0.45)
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=w * 0.55, radius2=0.05, depth=h * 0.55,
                              matrix=Matrix.Translation((x, y, base + h * 0.45 + h * 0.275)))

def gable_roof(part, x0, x1, y0, y1, z0, ridge, mat="roof"):
    """Pitched roof over a rectangle, ridge along x."""
    bm = bm_for(part, mat); ym = (y0 + y1) / 2
    poly(bm, [(x0, y0, z0), (x1, y0, z0), (x1, ym, ridge), (x0, ym, ridge)])
    poly(bm, [(x1, y1, z0), (x0, y1, z0), (x0, ym, ridge), (x1, ym, ridge)])

def lean_to(part, x0, x1, y_low, y_high, z_low, z_high, mat="roof"):
    poly(bm_for(part, mat), [(x0, y_low, z_low), (x1, y_low, z_low), (x1, y_high, z_high), (x0, y_high, z_high)])

def oct_dir(k):          # outward normal of octagon face k (k=0 east, 2 north, 4 west, 6 south)
    a = k * math.pi / 4; return Vector((math.cos(a), math.sin(a), 0))

def two_phase(fn, name, built, clad, *a):
    """Build a part twice: bare brick core from `built`, marble revetment from `clad` (cladding lagged the structure)."""
    global BARE
    if clad > built:
        BARE = True; fn(f"{name}_brick@{built}-{clad}", *a); BARE = False
    fn(f"{name}@{clad}-{NOW}", *a)


def export(name):
    """Create one object per (part, material), save blender/landmarks/<name>.blend, export the GLB and materials."""
    coll = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(coll)
    objs = []
    for (part, mname), bm in BMS.items():
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
        me = bpy.data.meshes.new(f"{part}.{mname}"); bm.to_mesh(me); bm.free(); me.validate(); me.update()
        o = bpy.data.objects.new(f"{part}.{mname}", me); coll.objects.link(o); o.data.materials.append(MAT[mname]); objs.append(o)
    blend = os.path.join(ROOT, "blender", "landmarks", f"{name}.blend"); os.makedirs(os.path.dirname(blend), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    for o in objs: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, f"{name}.glb"), export_format="GLB", use_selection=True, export_apply=True,
                              export_image_format="NONE", export_yup=True, export_normals=True)
    json.dump(MATDEF, open(os.path.join(OUT, f"{name}_materials.json"), "w", newline="\n"), indent=1)
    print(name.upper(), len(objs), "objects", sum(len(o.data.polygons) for o in objs), "faces")
    print("PARTS", sorted({o.name.split(".")[0] for o in objs}))

# octagonal helpers ---------------------------------------------------------------
def oct_face(k, apothem, z=0.0):
    """Frame on face k of an octagon (k=0 east, 2 north, …): u along the face from its left corner, n outward."""
    n = oct_dir(k); t = Vector((-n.y, n.x, 0)); half = apothem * T22
    return Frame(n * apothem - t * half + Vector((0, 0, z)), t, n), 2 * half
