"""Firenze Story – costume kit on the shared Mixamo skeleton (the Xbot placeholder figure).

Garments are cut from the body mesh by region (so they inherit its skin weights and follow every animation),
pushed out along the normals, decimated; skirts/robes are cones with weights transferred from the body.
Hats are static meshes attached to the head bone in the web app.

Run: blender -b --factory-startup --python blender/scripts/build_characters.py
Out: web/public/models/costumes.glb (Armature + skinned garments, no animations)
     web/public/models/hats.glb      (static headwear, metres, origin = top of the head)
Material names are tint slots for the web app: cloth_main, cloth_alt, linen, leather, metal.
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
XBOT = os.path.join(ROOT, "web", "public", "models", "Xbot.glb")
OUT = os.path.join(ROOT, "web", "public", "models")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=XBOT)
for a in list(bpy.data.actions): bpy.data.actions.remove(a)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = bpy.data.objects["Beta_Surface"]
if arm.animation_data: arm.animation_data_clear()
for o in bpy.data.objects:
    if o.type == "ARMATURE": o.data.pose_position = "REST"

def mat(name, rgb, rough=0.9, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    return m
M = {"cloth_main": mat("cloth_main", (0.5, 0.2, 0.15)), "cloth_alt": mat("cloth_alt", (0.3, 0.3, 0.4)),
     "linen": mat("linen", (0.85, 0.82, 0.74)), "leather": mat("leather", (0.3, 0.2, 0.12), 0.7),
     "metal": mat("metal", (0.55, 0.56, 0.58), 0.35, 1.0)}

MW = body.matrix_world.copy(); S = MW.to_scale()[0]                 # body local units -> metres

def from_body(name, keep, offset, material, ratio=0.22):
    """Copy the body, keep vertices where keep(world_pos) is True, inflate by `offset` metres, decimate."""
    ob = body.copy(); ob.data = body.data.copy(); ob.name = name; bpy.context.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
    kill = [v for v in bm.verts if not keep(MW @ v.co)]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    for v in bm.verts: v.co += v.normal * (offset / S)
    bm.to_mesh(ob.data); bm.free()
    ob.data.materials.clear(); ob.data.materials.append(M[material])
    for poly in ob.data.polygons: poly.use_smooth = True
    d = ob.modifiers.new("dec", "DECIMATE"); d.ratio = ratio
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier="dec")
    return ob

def cone(name, z_top, z_bot, r_top, r_bot, material, rx=1.0, ry=0.8, segs=18, rings=7, back_only=False):
    """Skirt / robe / cloak hanging from the waist or shoulders; skin weights copied from the body, biased to the hips."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rows = []
    for i in range(rings):
        t = i / (rings - 1); z = z_top + (z_bot - z_top) * t; r = r_top + (r_bot - r_top) * t
        a0, a1 = (math.pi * 0.08, math.pi * 0.92) if back_only else (0, 2 * math.pi)
        n = segs if not back_only else segs // 2 + 1
        row = []
        for k in range(n):
            a = a0 + (a1 - a0) * k / (n - (0 if not back_only else 1))
            row.append(bm.verts.new(((math.cos(a) * r * rx), (math.sin(a) * r * ry) + (0.02 if back_only else 0), z)))
        rows.append(row)
    for i in range(rings - 1):
        n = len(rows[i]); m_ = n if not back_only else n - 1
        for k in range(m_):
            bm.faces.new((rows[i][k], rows[i][(k + 1) % n], rows[i + 1][(k + 1) % n], rows[i + 1][k]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob.parent = arm; ob.matrix_parent_inverse = body.matrix_parent_inverse.copy()
    ob.matrix_basis = body.matrix_basis.copy()                       # same space as the body
    bpy.context.view_layer.update()
    inv = ob.matrix_world.inverted()
    for v in me.vertices: v.co = inv @ v.co                          # vertices were built in world metres
    me.materials.append(M[material])
    for poly in me.polygons: poly.use_smooth = True
    am = ob.modifiers.new("Armature", "ARMATURE"); am.object = arm
    # weights: nearest body surface, then bias to the hips so walking legs do not tear the cloth apart
    dt = ob.modifiers.new("dt", "DATA_TRANSFER"); dt.object = body; dt.use_vert_data = True
    dt.data_types_verts = {"VGROUP_WEIGHTS"}; dt.vert_mapping = "POLYINTERP_NEAREST"
    dt.layers_vgroup_select_src = "ALL"; dt.layers_vgroup_select_dst = "NAME"
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.datalayout_transfer(modifier="dt"); bpy.ops.object.modifier_apply(modifier="dt")
    hips = ob.vertex_groups.get("mixamorig:Hips") or ob.vertex_groups.new(name="mixamorig:Hips")
    spine = ob.vertex_groups.get("mixamorig:Spine2") or ob.vertex_groups.new(name="mixamorig:Spine2")
    for v in me.vertices:
        wz = (MW @ v.co).z
        hips.add([v.index], 0.9 if wz < 1.2 else 0.3, "ADD")
        if back_only and wz > 1.2: spine.add([v.index], 1.0, "ADD")
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    ob.select_set(False)
    return ob

ax = lambda p: abs(p.x)
# --- garments (world metres, T-pose: arms along x, feet at z=0, head top 1.78) ---
G = []
G.append(from_body("g_shirt", lambda p: 0.98 < p.z < 1.52 and ax(p) < 0.46, 0.012, "linen"))                                  # shirt / camicia, sleeves to the elbow
G.append(from_body("g_doublet", lambda p: 0.93 < p.z < 1.53 and ax(p) < 0.64, 0.02, "cloth_main"))                            # farsetto / giubbone, long sleeves
G.append(from_body("g_hose", lambda p: p.z < 1.05 and ax(p) < 0.24 and p.z > 0.07, 0.01, "cloth_alt"))                       # calze / hose / trousers
G.append(from_body("g_breeches", lambda p: 0.5 < p.z < 1.07 and ax(p) < 0.24, 0.028, "cloth_alt"))                          # brache (calcio, 16th–18th c.)
G.append(from_body("g_tunic", lambda p: 0.55 < p.z < 1.53 and ax(p) < 0.42, 0.03, "cloth_main"))                              # tunica (Roman, medieval)
G.append(from_body("g_boots", lambda p: p.z < 0.3 and ax(p) < 0.24, 0.015, "leather"))                                        # shoes / boots
G.append(from_body("g_bodice", lambda p: 0.98 < p.z < 1.5 and ax(p) < 0.6, 0.016, "cloth_main"))                              # women's bodice with sleeves
G.append(cone("g_skirt", 1.02, 0.05, 0.17, 0.36, "cloth_main"))                                                               # gonna / gamurra skirt
G.append(cone("g_robe", 1.05, 0.06, 0.18, 0.33, "cloth_main", rx=1.05, ry=0.85))                                              # lucco / long robe (citizens, clergy)
G.append(cone("g_apron", 1.0, 0.45, 0.17, 0.22, "linen", rx=1.0, ry=0.75, segs=18, rings=4))                                  # grembiule (front half kept below)
G.append(cone("g_cloak", 1.46, 0.4, 0.2, 0.34, "cloth_alt", back_only=True))                                                  # mantello
# the apron only covers the front: drop the back half
ap = bpy.data.objects["g_apron"]; bm = bmesh.new(); bm.from_mesh(ap.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if (MW @ v.co).y > -0.02], context="VERTS"); bm.to_mesh(ap.data); bm.free()

# --- headwear (static, metres, origin at the top of the head; attached to mixamorig:Head in the web app) ---
H = []
def hat(name, build, material, face=None):
    """face = (y, z): open the front below z (top-relative, metres) and ahead of y, so the face shows (hoods, helmets)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); build(bm)
    if face: bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().y < face[0] and f.calc_center_median().z < face[1]], context="FACES")
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); me.materials.append(M[material])
    for poly in me.polygons: poly.use_smooth = True
    H.append(ob); return ob
hat("h_beret", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.13,
    matrix=Matrix.Translation((0, -0.01, -0.02)) @ Matrix.Diagonal((1.15, 1.15, 0.45, 1))), "cloth_main")                  # berretta
hat("h_hood", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.135,
    matrix=Matrix.Translation((0, 0.01, -0.09)) @ Matrix.Diagonal((1.0, 1.08, 1.05, 1))), "cloth_alt", face=(-0.045, -0.03))                      # cappuccio / veil
def brim(bm):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=0.24, radius2=0.24, depth=0.012, matrix=Matrix.Translation((0, 0, -0.06)))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.11, radius2=0.1, depth=0.11, matrix=Matrix.Translation((0, 0, -0.01)))
hat("h_brim", brim, "leather")                                                                                              # wide-brimmed hat
hat("h_helmet", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.14,
    matrix=Matrix.Translation((0, 0, -0.07)) @ Matrix.Diagonal((1.0, 1.05, 0.9, 1))), "metal", face=(-0.055, -0.06))                               # bacinetto
def tophat(bm):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.17, radius2=0.17, depth=0.01, matrix=Matrix.Translation((0, 0, -0.05)))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.1, radius2=0.105, depth=0.17, matrix=Matrix.Translation((0, 0, 0.03)))
hat("h_tophat", tophat, "cloth_alt")                                                                                         # 19th-century hat

# --- heads: hair, beards and faces (static, same frame as the hats: origin at the HeadTop_End bone, metres) ---
# Built on the Xbot head surface so nothing pokes through: shells are copies of the head's own faces pushed out along
# the normals (hair caps, beards); the features are small convex hulls set on the surface found by ray casts.
from mathutils.bvhtree import BVHTree
import random
M.update({"skin": mat("skin", (0.78, 0.6, 0.48), 0.6), "hair": mat("hair", (0.18, 0.12, 0.08), 0.75),
          "eye_white": mat("eye_white", (0.86, 0.84, 0.8), 0.3), "iris": mat("iris", (0.12, 0.09, 0.07), 0.2),
          "lips": mat("lips", (0.62, 0.36, 0.33), 0.55)})
arm_ob = arm; bpy.context.view_layer.update()
TOP = arm_ob.matrix_world @ arm_ob.data.bones["mixamorig:HeadTop_End"].head_local
_me = body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
R3 = MW.to_3x3()
HV = [MW @ v.co for v in _me.vertices]; HN = [(R3 @ v.normal).normalized() for v in _me.vertices]
HP = [p.vertices[:] for p in _me.polygons]
BVH = BVHTree.FromPolygons(HV, HP)
def front(x, z, push=0.0):
    hit, n, i, d = BVH.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))
    return hit + n * push
def side(sx, y, z, push=0.0):
    hit, n, i, d = BVH.ray_cast(Vector((sx, y, z)), Vector((-sx, 0, 0)))
    return hit + n * push
def mesh_obj(name, bm, material):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); me.materials.append(M[material])
    for poly in me.polygons: poly.use_smooth = True
    H.append(ob); return ob
def hull(name, groups, material):
    """Convex hull of each point group (world coords), merged into one mesh, moved into the head-top frame."""
    bm = bmesh.new()
    for pts in groups:
        vs = [bm.verts.new(p - TOP) for p in pts]
        r = bmesh.ops.convex_hull(bm, input=vs)
        bmesh.ops.delete(bm, geom=list({g for g in r["geom_interior"] + r["geom_unused"] if isinstance(g, bmesh.types.BMVert) and g.is_valid}), context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, material)
CEN = Vector((0, -0.005, 1.665))
_dense = []                                        # dense sphere around the head projected onto its surface
_U, _V = 96, 48
for j in range(_V + 1):
    th = math.pi * j / _V
    row = []
    for i in range(_U):
        ph = 2 * math.pi * i / _U; d = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
        hit, n, _, _ = BVH.ray_cast(CEN, d, 0.3)
        row.append((hit, n) if hit is not None else None)
    _dense.append(row)
def shell(name, margin, offset, material, jitter=0.0, seed=1, feather=0.012):
    """Projected shell where margin(p) > 0 (metres inside the region); thinner towards the edge so it blends into the skin."""
    rnd = random.Random(seed); bm = bmesh.new(); vs = {}
    def vert(j, i):
        k = (j, i % _U)
        if k in vs: return vs[k]
        hit, n = _dense[j][i % _U]; m = margin(hit)
        o = offset * max(0.15, min(1.0, m / feather)) + (rnd.uniform(0, jitter) if jitter else 0.0)
        vs[k] = bm.verts.new(hit + n * o - TOP); return vs[k]
    for j in range(_V):
        for i in range(_U):
            q = [(j, i), (j, i + 1), (j + 1, i + 1), (j + 1, i)]
            cells = [_dense[a][b % _U] for a, b in q]
            if any(c is None for c in cells) or any(margin(c[0]) <= 0 for c in cells): continue
            try: bm.faces.new([vert(a, b) for a, b in q])
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, material)
def lerp(a, b, t): return a + (b - a) * max(0.0, min(1.0, t))
def hairline(front_z, temple_z, back_z, ear_top=1.695):
    """Margin above a line from the forehead past the temples to the nape, with a notch around each ear."""
    def m(p):
        zmin = lerp(front_z, temple_z, (p.y + 0.105) / 0.075) if p.y < -0.03 else lerp(temple_z, back_z, (p.y + 0.03) / 0.10)
        ear = max(0.052 - abs(p.x), abs(p.y + 0.004) - 0.034, p.z - ear_top)
        return min(p.z - zmin, ear)
    return m
# hair: cropped, short, curly, bob (to the jaw), long (to the shoulders), bun (gathered at the back), balding fringe
shell("hair_crop", hairline(1.75, 1.70, 1.61), 0.005, "hair")
shell("hair_short", hairline(1.744, 1.692, 1.595), 0.011, "hair")
shell("hair_curly", hairline(1.74, 1.69, 1.60), 0.016, "hair", jitter=0.008, seed=3)
shell("hair_bob", hairline(1.736, 1.64, 1.565, ear_top=1.60), 0.015, "hair")
_bh = hairline(1.80, 1.72, 1.60)
shell("hair_balding", lambda p: min(_bh(p), p.y + 0.03 if p.z > 1.76 else 1.0), 0.007, "hair")
base = shell("hair_long", hairline(1.736, 1.645, 1.555, ear_top=1.61), 0.015, "hair")
tail = hull("_tail", [[Vector((x, y, z)) for x in (-0.072, 0.072) for y in (0.045, 0.098) for z in (1.47, 1.66)] +
                      [Vector((0, 0.11, 1.62)), Vector((0, 0.095, 1.45))]], "hair")
bpy.ops.object.select_all(action="DESELECT"); base.select_set(True); tail.select_set(True)
bpy.context.view_layer.objects.active = base; H.remove(tail); bpy.ops.object.join()
bun_base = shell("hair_bun", hairline(1.738, 1.66, 1.58), 0.011, "hair")
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=9, radius=0.04, matrix=Matrix.Translation(Vector((0, 0.098, 1.672)) - TOP))
bun = mesh_obj("_bun", bm, "hair"); bpy.ops.object.select_all(action="DESELECT"); bun.select_set(True); bun_base.select_set(True)
bpy.context.view_layer.objects.active = bun_base; H.remove(bun); bpy.ops.object.join()
# beards and moustaches (men; fashions by era are chosen in the web app)
mouth = lambda p: max(abs(p.x) - 0.026, abs(p.z - 1.588) - 0.0115)
def beard(top_c, top_s, back):
    return lambda p: min(back - p.y, lerp(top_c, top_s, (abs(p.x) - 0.03) / 0.035) - p.z, p.z - 1.52, mouth(p))
shell("beard_full", beard(1.607, 1.648, 0.012), 0.011, "hair", jitter=0.003, seed=5, feather=0.008)
shell("beard_short", beard(1.580, 1.615, -0.01), 0.006, "hair", feather=0.006)
hull("beard_moustache", [[front(x, z, d) for x in (-0.03, -0.012, 0.012, 0.03) for z in (1.599, 1.607) for d in (0.002, 0.008)]], "hair")
# face: nose (3 shapes), brow ridge and ears in skin; eyes, irises, lips, brows
def face(name, tip, width, bridge):
    nose = [front(0, 1.682, 0.002), front(-bridge, 1.668, 0.002), front(bridge, 1.668, 0.002),
            front(0, 1.628, tip), front(0, 1.62, tip * 0.7), front(-width, 1.617, 0.004), front(width, 1.617, 0.004),
            front(-width * 0.6, 1.64, 0.008), front(width * 0.6, 1.64, 0.008), front(0, 1.614, 0.006)]
    brow = [[front(s * x, z, d) for x in (0.012, 0.03, 0.05) for z in (1.684, 1.694) for d in (0.0, 0.005 if z < 1.69 else 0.002)] for s in (-1, 1)]
    ears = []
    for s in (-1, 1):
        c = side(s, 0.004, 1.652)
        ears.append([c + Vector((s * (0.003 + 0.009 * math.cos(a) ** 2), 0.004 + 0.017 * math.cos(a), 0.031 * math.sin(a) - 0.004 * math.cos(a)))
                     for a in [k * math.pi / 8 for k in range(16)]] + [c + Vector((-s * 0.004, 0, 0))])
    chin = [front(x, z, d) for x in (-0.02, 0.02) for z in (1.552, 1.566) for d in (0.0, 0.006)]
    hull(name, [nose] + brow + ears + [chin], "skin")
face("f_face0", 0.020, 0.016, 0.006)       # straight
face("f_face1", 0.027, 0.019, 0.008)       # long, aquiline
face("f_face2", 0.015, 0.021, 0.008)       # short, broad
bm = bmesh.new()
for s in (-1, 1):
    c = front(s * 0.031, 1.665, -0.005)
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.0115, matrix=Matrix.Translation(c - TOP) @ Matrix.Diagonal((1.25, 0.55, 0.62, 1)))
mesh_obj("f_eyes", bm, "eye_white")
bm = bmesh.new()
for s in (-1, 1):
    c = front(s * 0.031, 1.665, 0.0005)
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.0058, matrix=Matrix.Translation(c - TOP) @ Matrix.Diagonal((1, 0.5, 1, 1)))
mesh_obj("f_iris", bm, "iris")
hull("f_lips", [[front(x, z, d) for x in (-0.022, -0.01, 0.01, 0.022) for z in (1.584, 1.592) for d in (0.0, 0.005 if abs(x) < 0.015 else 0.002)]], "lips")
hull("f_brows", [[front(s * x, z, d) for x in (0.014, 0.03, 0.048) for z in (1.689 + (0.002 if x == 0.03 else 0), 1.695) for d in (0.004, 0.008)] for s in (-1, 1)], "hair")

# --- export ---
def export(objs, path, skin):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    if skin: arm.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_animations=False,
                              export_skins=skin, export_image_format="NONE", export_yup=True)
export(G, os.path.join(OUT, "costumes.glb"), True)
export(H, os.path.join(OUT, "hats.glb"), False)
for o in G + H: print("GARMENT", o.name, len(o.data.vertices))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", "firenze_characters.blend"), compress=True)
