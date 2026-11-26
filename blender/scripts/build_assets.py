"""Firenze Story – reusable asset library, built reproducibly in Blender (>= 4.2, tested 5.3).

Run headless:   blender -b --factory-startup --python blender/scripts/build_assets.py
or through the Blender MCP (execute_blender_code_for_cli).

Outputs
  blender/firenze_assets.blend        library file (one collection per asset, shared materials)
  web/public/models/<asset>.glb       one GLB per asset, NO embedded images: materials are matched by name
                                      in the web app (fs_*), which binds the shared tileable textures from
                                      web/public/textures (built by pipeline/30_textures.py). One texture set,
                                      reused by city shader, props and Blender.
Conventions: metres, Z-up in Blender (glTF exporter converts to Y-up), origin at ground centre of the footprint,
front modelled towards +Y in Blender and exported facing +Z in three.js.
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEX = os.path.join(ROOT, "web", "public", "textures")
OUT = os.path.join(ROOT, "web", "public", "models")
BLEND = os.path.join(ROOT, "blender", "firenze_assets.blend")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.unit_settings.system = "METRIC"

# ---------------------------------------------------------------- materials
MATDEF = {}   # exported as models/materials.json – the web app rebuilds the same materials from it (single source)
def material(name, tex=None, color=(0.8, 0.8, 0.8), rough=0.85, scale=1.0, metal=0.0, tint=None):
    """Principled material. If tex is given, binds <tex>_col/_nrm/_rgh with box projection (object coords)."""
    tint = list(tint) if tint else [x / 0.85 for x in color] if tex in ("canvas", "intonaco") else [1.0, 1.0, 1.0]   # neutral textures get tinted
    MATDEF["fs_" + name] = {"tex": tex, "color": list(color), "tint": tint, "rough": rough, "scale": scale, "metal": metal}
    m = bpy.data.materials.new("fs_" + name)
    m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if tex and os.path.exists(os.path.join(TEX, tex + "_col.jpg")):
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
        nt.links.new(coord.outputs["Object"], mp.inputs["Vector"])
        def img(suffix, noncolor):
            n = nt.nodes.new("ShaderNodeTexImage")
            n.image = bpy.data.images.load(os.path.join(TEX, f"{tex}_{suffix}.jpg"), check_existing=True)
            n.projection = "BOX"; n.projection_blend = 0.2
            if noncolor: n.image.colorspace_settings.name = "Non-Color"
            nt.links.new(mp.outputs["Vector"], n.inputs["Vector"]); return n
        c = img("col", False); r = img("rgh", True); n = img("nrm", True)
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(c.outputs["Color"], mix.inputs["A"]); mix.inputs["B"].default_value = (*tint, 1)
        nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
        nt.links.new(r.outputs["Color"], bsdf.inputs["Roughness"])
        nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(n.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return m

M = {
    "wood":      material("wood", "wood", (0.45, 0.34, 0.24), 0.8, 1.0),
    "wood_dark": material("wood_dark", "wood", (0.25, 0.18, 0.12), 0.8, 1.0, tint=(0.55, 0.5, 0.45)),
    "canvas":    material("canvas", "canvas", (0.85, 0.80, 0.68), 0.9, 2.0),
    "canvas_red":material("canvas_red", "canvas", (0.55, 0.16, 0.12), 0.9, 2.0),
    "canvas_blu":material("canvas_blu", "canvas", (0.22, 0.30, 0.45), 0.9, 2.0),
    "wicker":    material("wicker", None, (0.62, 0.48, 0.28), 0.95),
    "terracotta":material("terracotta", "cotto", (0.70, 0.40, 0.26), 0.85, 1.5),
    "iron":      material("iron", None, (0.18, 0.18, 0.19), 0.5, metal=0.8),
    "gold":      material("gold", None, (0.85, 0.65, 0.25), 0.35, metal=1.0),
    "red_paint": material("red_paint", None, (0.55, 0.08, 0.06), 0.6),
    "white":     material("white", None, (0.92, 0.91, 0.88), 0.7),
    "produce_g": material("produce_green", None, (0.30, 0.45, 0.15), 0.7),
    "produce_o": material("produce_orange", None, (0.85, 0.45, 0.10), 0.6),
    "produce_r": material("produce_red", None, (0.60, 0.10, 0.08), 0.6),
    "bread":     material("bread", None, (0.72, 0.52, 0.28), 0.9),
    "cloth":     material("cloth_bolt", "canvas", (0.40, 0.18, 0.35), 0.9, 3.0),
    "sand":      material("sand", None, (0.72, 0.64, 0.48), 1.0),
    "thatch":    material("thatch", None, (0.52, 0.44, 0.28), 1.0),
    "daub":      material("daub", None, (0.55, 0.45, 0.33), 1.0),
    "feather_w": material("feather_white", None, (0.9, 0.9, 0.88), 0.9),
    "feather_g": material("feather_grey", None, (0.45, 0.47, 0.48), 0.9),
    "duck":      material("duck_brown", None, (0.36, 0.28, 0.2), 0.8),
    "fur":       material("fur_deer", None, (0.45, 0.3, 0.18), 1.0),
    "dark":      material("bird_dark", None, (0.12, 0.12, 0.14), 0.8),
    "clay":      material("clay", None, (0.62, 0.42, 0.30), 0.95),
    "stone":     material("stone_serena", "pietra_serena", (0.55, 0.56, 0.55), 0.9, 1.0),
    "wool":      material("wool", None, (0.82, 0.79, 0.72), 1.0),
    "pig":       material("pig_dark", None, (0.30, 0.24, 0.22), 0.9),
    "cow":       material("cow", None, (0.58, 0.50, 0.40), 0.95),
    "ember":     material("ember", None, (0.9, 0.35, 0.08), 0.6),
}

# ---------------------------------------------------------------- primitives (bmesh, applied)
def obj(name, coll, mat, build):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); coll.objects.link(o)
    o.data.materials.append(mat)
    for p in me.polygons: p.use_smooth = False
    return o

def box(bm, c, s, rot_z=0.0, rot_y=0.0):
    r = bmesh.ops.create_cube(bm, size=1.0)
    m = Matrix.Translation(c) @ Matrix.Rotation(rot_z, 4, "Z") @ Matrix.Rotation(rot_y, 4, "Y") @ Matrix.Diagonal((*s, 1))
    bmesh.ops.transform(bm, matrix=m, verts=r["verts"])

def cyl(bm, c, r1, r2, h, seg=12, axis="Z", rot_z=0.0):
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h)
    rot = Matrix.Identity(4) if axis == "Z" else Matrix.Rotation(math.pi / 2, 4, "X" if axis == "Y" else "Y")
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ Matrix.Rotation(rot_z, 4, "Z") @ rot, verts=r["verts"])

def lathe(bm, profile, seg=16, c=(0, 0, 0)):
    """Revolve a (radius, z) profile around Z – barrels, jars, baskets."""
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        rings.append([bm.verts.new((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2] + z)) for r, z in profile])
    for i in range(seg):
        A, B = rings[i], rings[(i + 1) % seg]
        for j in range(len(profile) - 1):
            bm.faces.new((A[j], B[j], B[j + 1], A[j + 1]))
    bm.faces.new([r[0] for r in reversed(rings)])

def new_coll(name):
    c = bpy.data.collections.new(name); scn.collection.children.link(c); return c

ASSETS = {}
def asset(fn):
    ASSETS[fn.__name__] = fn; return fn

# ---------------------------------------------------------------- props
@asset
def barrel(c):                                    # botte, 0.9 m
    p = [(0.0, 0), (0.30, 0), (0.30, 0.02)] + [(0.30 + 0.06 * math.sin(math.pi * t / 8), 0.02 + 0.86 * t / 8) for t in range(1, 8)] + [(0.30, 0.88), (0.0, 0.88)]
    obj("barrel", c, M["wood_dark"], lambda bm: lathe(bm, p, 18))
    def hoops(bm):
        for z in (0.12, 0.30, 0.58, 0.76):
            r = 0.30 + 0.06 * math.sin(math.pi * z / 0.88) + 0.008
            cyl(bm, (0, 0, z), r, r, 0.035, 18)
    obj("barrel_hoops", c, M["iron"], hoops)

@asset
def basket(c):                                    # cesta, wicker with produce
    p = [(0.0, 0), (0.18, 0), (0.24, 0.10), (0.27, 0.26), (0.26, 0.28), (0.22, 0.10), (0.0, 0.04)]
    obj("basket", c, M["wicker"], lambda bm: lathe(bm, p, 16))
    def fruit(bm):
        import random; R = random.Random(3)
        for i in range(14):
            a, r = R.random() * 6.28, R.random() * 0.17
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.05, matrix=Matrix.Translation((r * math.cos(a), r * math.sin(a), 0.22 + R.random() * 0.06)))
    obj("basket_fruit", c, M["produce_o"], fruit)

@asset
def crate(c):                                     # cassetta, open slatted
    def b(bm):
        for x in (-0.28, 0.28): box(bm, (x, 0, 0.15), (0.03, 0.4, 0.3))
        for y in (-0.19, 0.19):
            for z in (0.06, 0.22): box(bm, (0, y, z), (0.6, 0.02, 0.1))
        box(bm, (0, 0, 0.01), (0.6, 0.4, 0.02))
    obj("crate", c, M["wood"], b)
    def veg(bm):
        for i in range(12):
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.06, matrix=Matrix.Translation((-0.2 + (i % 4) * 0.13, -0.11 + (i // 4) * 0.11, 0.27)))
    obj("crate_veg", c, M["produce_g"], veg)

@asset
def jar(c):                                       # orcio – oil jar
    p = [(0.0, 0), (0.14, 0), (0.30, 0.25), (0.33, 0.45), (0.25, 0.72), (0.13, 0.82), (0.15, 0.86), (0.12, 0.88), (0.0, 0.85)]
    obj("jar", c, M["terracotta"], lambda bm: lathe(bm, p, 18))

@asset
def bench(c):                                     # panca
    def b(bm):
        box(bm, (0, 0, 0.44), (1.8, 0.32, 0.05))
        for x in (-0.75, 0.75): box(bm, (x, 0, 0.21), (0.06, 0.28, 0.42))
    obj("bench", c, M["wood"], b)

@asset
def table(c):                                     # tavola da taverna
    def b(bm):
        box(bm, (0, 0, 0.76), (1.6, 0.7, 0.05))
        for x in (-0.7, 0.7):
            for y in (-0.28, 0.28): box(bm, (x, y, 0.37), (0.07, 0.07, 0.74))
    obj("table", c, M["wood_dark"], b)
    def food(bm):
        cyl(bm, (-0.3, 0, 0.82), 0.12, 0.10, 0.06, 12); cyl(bm, (0.35, 0.1, 0.84), 0.05, 0.04, 0.12, 8)
    obj("table_food", c, M["bread"], food)

def stall_frame(c, awning_mat, goods):
    """Banco del mercato: trestle counter, 4 posts, sloped canvas awning, goods on top."""
    W, D, H = 2.4, 1.2, 0.9
    def frame(bm):
        box(bm, (0, 0, H), (W, D, 0.06))                                    # counter
        box(bm, (0, D / 2 - 0.02, H / 2), (W, 0.03, H - 0.05))              # front board
        for x in (-W / 2 + 0.05, W / 2 - 0.05):
            box(bm, (x, D / 2 - 0.05, 1.15), (0.07, 0.07, 2.3))             # front posts 2.3 m
            box(bm, (x, -D / 2 + 0.05, 1.4), (0.07, 0.07, 2.8))             # back posts 2.8 m
    obj("stall_frame", c, M["wood"], frame)
    def awn(bm):
        verts = [bm.verts.new(v) for v in [(-W / 2 - 0.15, D / 2 + 0.35, 2.2), (W / 2 + 0.15, D / 2 + 0.35, 2.2),
                                            (W / 2 + 0.15, -D / 2, 2.85), (-W / 2 - 0.15, -D / 2, 2.85)]]
        f = bm.faces.new(verts)
        bmesh.ops.solidify(bm, geom=[f], thickness=0.02)
        # scalloped valance
        for i in range(8):
            x = -W / 2 - 0.15 + (i + 0.5) * (W + 0.3) / 8
            box(bm, (x, D / 2 + 0.35, 2.1), ((W + 0.3) / 8 * 0.92, 0.01, 0.2))
    obj("stall_awning", c, awning_mat, awn)
    goods(c, H)

@asset
def stall_produce(c):
    def g(c, H):
        def b(bm):
            import random; R = random.Random(7)
            for i in range(40):
                bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.06, matrix=Matrix.Translation((R.uniform(-1.05, 1.05), R.uniform(-0.45, 0.45), H + 0.07 + R.random() * 0.05)))
        obj("goods_produce", c, M["produce_r"], b)
    stall_frame(c, M["canvas"], g)

@asset
def stall_cloth(c):                               # Arte della Lana / Calimala – bolts of cloth
    def g(c, H):
        def b(bm):
            for i in range(7): cyl(bm, (-0.9 + i * 0.3, 0, H + 0.1), 0.09, 0.09, 0.9, 10, axis="Y")
        obj("goods_cloth", c, M["cloth"], b)
    stall_frame(c, M["canvas_blu"], g)

@asset
def stall_bread(c):
    def g(c, H):
        def b(bm):
            for i in range(18):
                bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.09,
                                          matrix=Matrix.Translation((-1.0 + (i % 9) * 0.25, -0.2 + (i // 9) * 0.4, H + 0.06)) @ Matrix.Diagonal((1.3, 1, 0.55, 1)))
        obj("goods_bread", c, M["bread"], b)
    stall_frame(c, M["canvas_red"], g)

@asset
def tribune(c):                                   # wooden stand module for calcio storico (6 m x 4 tiers)
    def b(bm):
        for t in range(4):
            box(bm, (0, -t * 0.7, 0.45 + t * 0.45), (6.0, 0.7, 0.06))        # seat boards
            box(bm, (0, -t * 0.7 + 0.32, 0.22 + t * 0.45), (6.0, 0.04, 0.45))  # risers
        for x in (-2.9, -1.0, 1.0, 2.9):
            for t in range(4): box(bm, (x, -t * 0.7, (0.45 + t * 0.45) / 2), (0.1, 0.1, 0.45 + t * 0.45))
    obj("tribune", c, M["wood"], b)
    def drape(bm): box(bm, (0, 0.38, 0.3), (6.0, 0.02, 0.55))
    obj("tribune_drape", c, M["canvas_red"], drape)

@asset
def brindellone(c):
    """Carro del Brindellone (1622 cart): 4 wheels, painted base, 3 tapering tiers with pyrotechnic tower, ~ 9 m."""
    def wheels(bm):
        for x in (-1.3, 1.3):
            for y in (-0.95, 0.95): cyl(bm, (x, y, 0.65), 0.65, 0.65, 0.12, 20, axis="Y")
    obj("brindellone_wheels", c, M["wood_dark"], wheels)
    def body(bm):
        box(bm, (0, 0, 1.25), (3.4, 1.8, 0.35))                                # chassis
        box(bm, (0, 0, 2.2), (2.8, 1.6, 1.6))                                  # painted base
        box(bm, (0, 0, 3.55), (2.2, 1.3, 1.1))                                 # tier 2
        box(bm, (0, 0, 4.7), (1.5, 1.0, 1.2))                                  # tier 3
        cyl(bm, (0, 0, 6.2), 0.55, 0.25, 1.8, 8)                               # spire
    obj("brindellone_body", c, M["red_paint"], body)
    def gilt(bm):
        for z, sx, sy in ((3.0, 2.9, 1.7), (4.1, 2.3, 1.4), (5.3, 1.6, 1.1)): box(bm, (0, 0, z), (sx, sy, 0.1))   # cornices
        for x in (-1.0, 1.0):
            for y in (-0.6, 0.6): cyl(bm, (x * 0.9, y * 0.85, 3.55), 0.06, 0.06, 1.1, 8)                         # pilasters
        cyl(bm, (0, 0, 7.4), 0.05, 0.05, 0.7, 6); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.25, matrix=Matrix.Translation((0, 0, 7.85)))
    obj("brindellone_gilt", c, M["gold"], gilt)
    def panels(bm):
        for y in (-0.81, 0.81): box(bm, (0, y, 2.2), (2.2, 0.02, 1.1))         # white heraldic panels (giglio drawn in shader later)
    obj("brindellone_panels", c, M["white"], panels)

@asset
def colombina(c):
    """Dove-shaped rocket that runs along the wire from the altar to the cart (~0.4 m)."""
    def b(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.08, matrix=Matrix.Diagonal((2.2, 1, 1, 1)))    # body
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.05, matrix=Matrix.Translation((0.2, 0, 0.04)))              # head
        for s in (-1, 1):
            v = [bm.verts.new(p) for p in [(0.05, s * 0.05, 0.02), (-0.08, s * 0.05, 0.02), (-0.02, s * 0.28, 0.06)]]
            bm.faces.new(v if s > 0 else list(reversed(v)))                                                                # wings
        v = [bm.verts.new(p) for p in [(-0.15, 0, 0), (-0.3, 0.07, 0.02), (-0.3, -0.07, 0.02)]]; bm.faces.new(v)          # tail
    obj("colombina", c, M["white"], b)
    obj("colombina_rocket", c, M["iron"], lambda bm: cyl(bm, (0, 0, -0.09), 0.025, 0.025, 0.25, 8, axis="X"))

# ---------------------------------------------------------------- river (Comune di Firenze, "Una città e il suo fiume", 2019)
def hull(bm, L, W, H, bow=0.25, rise=0.25):
    """Flat-bottomed river boat hull (barchetto / navicello / scafa): open, pointed bow raised, square stern."""
    n = 9; top, bot = [], []
    for i in range(n):
        t = i / (n - 1); x = -L / 2 + L * t
        w = W / 2 * (1 - max(0, (t - (1 - bow)) / bow) ** 1.6)                 # taper towards the bow (+x)
        lift = rise * max(0, (t - 0.7) / 0.3) ** 2
        bot += [bm.verts.new((x, -w * 0.82, lift)), bm.verts.new((x, w * 0.82, lift))]
        top += [bm.verts.new((x, -w, H + lift)), bm.verts.new((x, w, H + lift))]
    for i in range(n - 1):
        a, b = 2 * i, 2 * i + 2
        bm.faces.new((bot[a], bot[b], bot[b + 1], bot[a + 1]))                  # bottom
        bm.faces.new((bot[a], top[a], top[b], bot[b]))                          # sides
        bm.faces.new((bot[a + 1], bot[b + 1], top[b + 1], top[a + 1]))
    bm.faces.new((bot[0], bot[1], top[1], top[0]))                              # transom
    bm.faces.new((bot[-2], top[-2], top[-1], bot[-1]))

@asset
def barchetto(c):                                 # renaioli sand boat, ~6.5 m, poled
    obj("barchetto", c, M["wood_dark"], lambda bm: hull(bm, 6.5, 1.6, 0.45))
    obj("barchetto_sand", c, M["sand"], lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=6, radius=1.0,
        matrix=Matrix.Translation((-0.4, 0, 0.18)) @ Matrix.Diagonal((1.9, 0.55, 0.3, 1))))
    obj("barchetto_pole", c, M["wood"], lambda bm: cyl(bm, (0.6, 0.55, 1.6), 0.03, 0.03, 5.0, 6, axis="Y", rot_z=0.0) if False else
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.03, radius2=0.03, depth=5.0,
                              matrix=Matrix.Translation((2.4, 0.5, 1.4)) @ Matrix.Rotation(1.25, 4, "Y")))

@asset
def navicello(c):                                 # cargo boat with mast and square sail, ~13 m
    obj("navicello", c, M["wood_dark"], lambda bm: hull(bm, 13.0, 3.0, 0.9, bow=0.2, rise=0.4))
    def rig(bm):
        cyl(bm, (0.5, 0, 4.6), 0.08, 0.06, 8.0, 8)                              # mast
        cyl(bm, (0.5, 0, 7.6), 0.05, 0.05, 4.2, 6, axis="Y")                    # yard
    obj("navicello_rig", c, M["wood"], rig)
    obj("navicello_sail", c, M["canvas"], lambda bm: box(bm, (0.6, 0, 5.6), (0.04, 4.0, 3.6)))
    def cargo(bm):
        for i in range(4): box(bm, (-3.5 + i * 1.5, 0, 1.0), (1.2, 2.0, 0.7))    # bales / barrels of goods
    obj("navicello_cargo", c, M["canvas_blu"], cargo)

@asset
def scafa(c):                                     # ferry barge (passo di barca) with rails, ~8 m
    obj("scafa", c, M["wood_dark"], lambda bm: hull(bm, 8.0, 3.0, 0.5, bow=0.12, rise=0.1))
    def rails(bm):
        for s in (-1, 1): box(bm, (0, s * 1.45, 1.1), (6.8, 0.06, 0.06))
        for s in (-1, 1):
            for i in range(5): box(bm, (-3.2 + i * 1.6, s * 1.45, 0.8), (0.07, 0.07, 0.6))
    obj("scafa_rails", c, M["wood"], rails)

@asset
def scalo(c):                                     # wooden landing stage on piles (scalo / porticciola)
    def deck(bm):
        box(bm, (0, 0, 0.55), (8.0, 3.0, 0.12))
        for x in (-3.6, -1.2, 1.2, 3.6):
            for y in (-1.3, 1.3): box(bm, (x, y, -0.6), (0.18, 0.18, 2.4))
        for i in range(4): box(bm, (0, -1.5 - 0.35 * i, 0.4 - 0.25 * i), (2.0, 0.35, 0.08))   # steps up the bank
    obj("scalo", c, M["wood"], deck)

@asset
def sandheap(c):                                  # mound of river sand drying on the bank (renai)
    obj("sandheap", c, M["sand"], lambda bm: bmesh.ops.create_cone(bm, cap_ends=False, segments=14, radius1=2.2, radius2=0.3, depth=1.4,
        matrix=Matrix.Translation((0, 0, 0.7))))

# ---------------------------------------------------------------- wildlife
@asset
def duck(c):
    def b(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.16, matrix=Matrix.Diagonal((1.6, 1, 0.7, 1)))
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.07, matrix=Matrix.Translation((0.22, 0, 0.14)))
    obj("duck", c, M["duck"], b)

@asset
def heron(c):                                     # grey heron standing in the shallows
    def b(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.2, matrix=Matrix.Translation((0, 0, 0.75)) @ Matrix.Diagonal((1.5, 0.8, 0.9, 1)))
        cyl(bm, (0.2, 0, 1.05), 0.035, 0.03, 0.45, 6, axis="Y", rot_z=0); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.06, matrix=Matrix.Translation((0.25, 0, 1.3)))
    obj("heron", c, M["feather_g"], b)
    def legs(bm):
        for s in (-1, 1): cyl(bm, (0, s * 0.06, 0.32), 0.012, 0.012, 0.64, 5)
        cyl(bm, (0.42, 0, 1.3), 0.012, 0.0, 0.2, 5, axis="X")
    obj("heron_legs", c, M["dark"], legs)

@asset
def bird(c):                                      # swallow / swift silhouette for flocks (wings animated in the web app)
    def b(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=0.05, matrix=Matrix.Diagonal((2.2, 0.8, 0.8, 1)))
        for s in (-1, 1):
            v = [bm.verts.new(p) for p in [(0.04, 0, 0), (-0.04, 0, 0), (-0.06, s * 0.22, 0.01)]]
            bm.faces.new(v if s > 0 else list(reversed(v)))
    obj("bird", c, M["dark"], b)

@asset
def deer(c):                                      # red deer (pre-urban woods and meadows)
    def b(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.45, matrix=Matrix.Translation((0, 0, 1.0)) @ Matrix.Diagonal((1.6, 0.75, 0.8, 1)))
        cyl(bm, (0.75, 0, 1.35), 0.12, 0.09, 0.6, 6, axis="Y"); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.14,
            matrix=Matrix.Translation((0.95, 0, 1.62)) @ Matrix.Diagonal((1.6, 0.8, 0.8, 1)))
        for x in (-0.5, 0.5):
            for y in (-0.18, 0.18): cyl(bm, (x, y, 0.4), 0.05, 0.04, 0.8, 5)
    obj("deer", c, M["fur"], b)

# ---------------------------------------------------------------- Iron Age (Villanovan) hut – after excavated hut plans in Etruria: oval, posts, wattle-and-daub, thatch
@asset
def hut(c):
    def wall(bm):
        p = [(math.cos(a) * 3.6, math.sin(a) * 2.4) for a in [i / 20 * 2 * math.pi for i in range(20)]]
        lo = [bm.verts.new((x, y, 0)) for x, y in p]; hi = [bm.verts.new((x, y, 1.1)) for x, y in p]
        for i in range(20):
            j = (i + 1) % 20
            if i in (4, 5): continue                                              # doorway (south side)
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    obj("hut_wall", c, M["daub"], wall)
    def roof(bm):
        p = [(math.cos(a) * 4.2, math.sin(a) * 2.9) for a in [i / 20 * 2 * math.pi for i in range(20)]]
        eave = [bm.verts.new((x, y, 0.95)) for x, y in p]
        ridge = [bm.verts.new((x * 0.35, 0, 4.6)) for x, y in p]
        for i in range(20):
            j = (i + 1) % 20; bm.faces.new((eave[i], eave[j], ridge[j], ridge[i]))
    obj("hut_roof", c, M["thatch"], roof)

@asset
def palisade(c):                                  # 6 m of stakes
    def b(bm):
        for i in range(24): cyl(bm, (-3 + i * 0.25, 0, 0.9), 0.09, 0.07, 1.8 + 0.2 * math.sin(i * 1.7), 6)
    obj("palisade", c, M["wood_dark"], b)

# ---------------------------------------------------------------- Villanovan / Etruscan life (docs/HISTORY.md, "Before Florentia")
@asset
def hut_stilt(c):                                 # oval hut on a raised platform (marshy plain, floods): florencecity.it, Villanovan Florence
    def deck(bm):
        box(bm, (0, 0, 0.75), (8.4, 5.6, 0.14))
        for x in (-3.6, -1.2, 1.2, 3.6):
            for y in (-2.3, 0, 2.3): cyl(bm, (x, y, 0.3), 0.12, 0.12, 1.0, 6)
        for i in range(5): box(bm, (0.9 + 0.0, -3.2 - 0.25 * i, 0.62 - 0.14 * i), (1.0, 0.22, 0.05))   # ladder-steps to the door
    obj("hut_stilt_deck", c, M["wood_dark"], deck)
    def wall(bm):
        p = [(math.cos(a) * 3.6, math.sin(a) * 2.4) for a in [i / 20 * 2 * math.pi for i in range(20)]]
        lo = [bm.verts.new((x, y, 0.82)) for x, y in p]; hi = [bm.verts.new((x, y, 1.95)) for x, y in p]
        for i in range(20):
            j = (i + 1) % 20
            if i in (14, 15): continue                                            # doorway towards the ladder
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    obj("hut_stilt_wall", c, M["daub"], wall)
    def roof(bm):
        p = [(math.cos(a) * 4.2, math.sin(a) * 2.9) for a in [i / 20 * 2 * math.pi for i in range(20)]]
        eave = [bm.verts.new((x, y, 1.8)) for x, y in p]
        ridge = [bm.verts.new((x * 0.35, 0, 5.3)) for x, y in p]
        for i in range(20):
            j = (i + 1) % 20; bm.faces.new((eave[i], eave[j], ridge[j], ridge[i]))
    obj("hut_stilt_roof", c, M["thatch"], roof)

@asset
def kiln(c):                                      # updraft pottery kiln (clay dome, stoke hole) – Villanovan / Etruscan workshops
    def dome(bm):
        p = [(0.0, 0), (1.3, 0), (1.35, 0.5), (1.2, 1.1), (0.8, 1.6), (0.25, 1.85), (0.0, 1.85)]
        lathe(bm, p, 14)
        box(bm, (1.45, 0, 0.3), (0.6, 0.5, 0.6))                                 # stoke hole
    obj("kiln", c, M["clay"], dome)
    obj("kiln_fire", c, M["ember"], lambda bm: box(bm, (1.76, 0, 0.25), (0.05, 0.35, 0.3)))
    def pots(bm):
        for i in range(5):
            a = i * 1.2; lathe(bm, [(0.0, 0), (0.12, 0), (0.2, 0.15), (0.12, 0.32), (0.09, 0.36), (0.0, 0.36)], 10, c=(-1.9 + math.cos(a) * 0.4, math.sin(a) * 0.5, 0))
    obj("kiln_pots", c, M["terracotta"], pots)

@asset
def hearth(c):                                    # open fire ring with a pot on the embers
    def ring(bm):
        for i in range(9): bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=0.18, matrix=Matrix.Translation((math.cos(i / 9 * 6.283) * 0.6, math.sin(i / 9 * 6.283) * 0.6, 0.08)))
    obj("hearth", c, M["stone"], ring)
    obj("hearth_fire", c, M["ember"], lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.4, radius2=0.05, depth=0.35, matrix=Matrix.Translation((0, 0, 0.18))))

@asset
def canoe(c):                                     # monoxylon dugout (Arno, Iron Age), ~6 m, with jars of goods
    obj("canoe", c, M["wood_dark"], lambda bm: hull(bm, 6.0, 0.9, 0.42, bow=0.3, rise=0.15))
    def jars(bm):
        for i in range(3): lathe(bm, [(0.0, 0), (0.12, 0), (0.22, 0.2), (0.14, 0.45), (0.08, 0.5), (0.0, 0.5)], 10, c=(-1.5 + i * 0.8, 0, 0.05))
    obj("canoe_jars", c, M["terracotta"], jars)

def quadruped(bm, L, H, W, head=0.25):
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.5, matrix=Matrix.Translation((0, 0, H)) @ Matrix.Diagonal((L, W, H * 0.45, 1)))
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=head, matrix=Matrix.Translation((L * 0.58, 0, H * 1.12)) @ Matrix.Diagonal((1.4, 0.8, 0.85, 1)))
    for x in (-L * 0.33, L * 0.33):
        for y in (-W * 0.25, W * 0.25): cyl(bm, (x, y, H * 0.35), 0.045 * (1 + L), 0.035 * (1 + L), H * 0.7, 5)

@asset
def sheep(c):
    obj("sheep", c, M["wool"], lambda bm: quadruped(bm, 1.0, 0.6, 0.55, 0.13))

@asset
def pig(c):
    obj("pig", c, M["pig"], lambda bm: quadruped(bm, 1.1, 0.45, 0.5, 0.15))

@asset
def cow(c):                                       # small Iron Age cattle (also draught oxen)
    obj("cow", c, M["cow"], lambda bm: quadruped(bm, 1.9, 1.0, 0.75, 0.22))

@asset
def urn_grave(c):                                 # cremation pit grave with biconical urn and small cairn (Villanovan necropolis)
    def cairn(bm):
        for i in range(7): bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=0.22, matrix=Matrix.Translation((math.cos(i) * 0.45, math.sin(i * 1.3) * 0.45, 0.1)))
    obj("urn_grave", c, M["stone"], cairn)
    obj("urn_grave_urn", c, M["terracotta"], lambda bm: lathe(bm, [(0.0, 0), (0.1, 0), (0.24, 0.22), (0.12, 0.42), (0.14, 0.5), (0.0, 0.5)], 12, c=(0, 0, 0.1)))

@asset
def stele(c):                                     # Fiesolan archaic stele (horseshoe top, pietra serena), 6th–5th c. BC
    def b(bm):
        box(bm, (0, 0, 0.6), (0.62, 0.16, 1.2))
        cyl(bm, (0, 0, 1.2), 0.31, 0.31, 0.16, 14, axis="Y")
    obj("stele", c, M["stone"], b)

# ---------------------------------------------------------------- build, save, export
for name, fn in ASSETS.items():
    coll = new_coll(name); fn(coll)

bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True)

# Export convention: the modelled "front" is +Y in Blender; turn 180° so that it becomes +Z in three.js (glTF).
for o in bpy.data.objects: o.data.transform(Matrix.Rotation(math.pi, 4, "Z"))
for name in ASSETS:
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.data.collections[name].objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, name + ".glb"), export_format="GLB", use_selection=True,
                              export_apply=True, export_image_format="NONE", export_yup=True)
    n = sum(len(o.data.polygons) for o in bpy.data.collections[name].objects)
    print(f"ASSET {name}: {len(bpy.data.collections[name].objects)} parts, {n} faces")
import json
json.dump(MATDEF, open(os.path.join(OUT, "materials.json"), "w", newline="\n"), indent=1)
print("BLEND", BLEND)
