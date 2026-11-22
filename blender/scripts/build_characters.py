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
def hat(name, build, material):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); me.materials.append(M[material])
    for poly in me.polygons: poly.use_smooth = True
    H.append(ob); return ob
hat("h_beret", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.13,
    matrix=Matrix.Translation((0, -0.01, -0.02)) @ Matrix.Diagonal((1.15, 1.15, 0.45, 1))), "cloth_main")                  # berretta
hat("h_hood", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.135,
    matrix=Matrix.Translation((0, 0.01, -0.09)) @ Matrix.Diagonal((1.0, 1.08, 1.05, 1))), "cloth_alt")                      # cappuccio / veil
def brim(bm):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=0.24, radius2=0.24, depth=0.012, matrix=Matrix.Translation((0, 0, -0.06)))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.11, radius2=0.1, depth=0.11, matrix=Matrix.Translation((0, 0, -0.01)))
hat("h_brim", brim, "leather")                                                                                              # wide-brimmed hat
hat("h_helmet", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.14,
    matrix=Matrix.Translation((0, 0, -0.07)) @ Matrix.Diagonal((1.0, 1.05, 0.9, 1))), "metal")                               # bacinetto
def tophat(bm):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.17, radius2=0.17, depth=0.01, matrix=Matrix.Translation((0, 0, -0.05)))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.1, radius2=0.105, depth=0.17, matrix=Matrix.Translation((0, 0, 0.03)))
hat("h_tophat", tophat, "cloth_alt")                                                                                         # 19th-century hat

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
