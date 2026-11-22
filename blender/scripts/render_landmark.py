"""Preview renders of a dated landmark model at a given year:
blender -b blender/landmarks/duomo.blend --python blender/scripts/render_landmark.py -- <year> <out_prefix> [views]"""
import bpy, math, sys
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
year = float(args[0]); out = args[1]
views = args[2].split(",") if len(args) > 2 else ["nw", "se", "sw_low", "top"]
sc = bpy.context.scene
for o in bpy.data.objects:
    if "@" in o.name:
        a, b = o.name.split("@")[1].split(".")[0].split("-")
        o.hide_render = not (float(a) <= year < float(b))
w = bpy.data.worlds.new("sky"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.62, 0.72, 0.85, 1); bg.inputs[1].default_value = 0.9
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(200)); sun.data.energy = 3.5; sun.data.angle = 0.05
ground = bpy.data.meshes.new("g"); ground.from_pydata([(-400, -400, -0.05), (400, -400, -0.05), (400, 400, -0.05), (-400, 400, -0.05)], [], [(0, 1, 2, 3)])
go = bpy.data.objects.new("ground", ground); sc.collection.objects.link(go)
gm = bpy.data.materials.new("ground"); gm.use_nodes = True; gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.42, 0.38, 0.33, 1); go.data.materials.append(gm)
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x = 1280; sc.render.resolution_y = 800
try: sc.eevee.use_shadows = True
except Exception: pass
CAMS = {   # (azimuth from east, elevation, distance, target z)
    "nw": (140, 18, 260, 45), "se": (-40, 22, 250, 45), "sw_low": (-150, 6, 190, 35), "top": (200, 60, 300, 40),
    "facade": (180, 4, 120, 25), "dome": (120, 25, 140, 80), "north": (90, 8, 200, 35),
    # smaller monuments (origin at the centre): near_* look at x = 0
    "near_nw": (135, 12, 95, 22), "near_se": (-45, 10, 90, 20), "near_w": (180, 6, 70, 14), "tall_sw": (-140, 10, 170, 45),
}
for v in views:
    az, el, d, tz = CAMS[v]
    cam = bpy.data.objects.new("cam_" + v, bpy.data.cameras.new("cam_" + v)); sc.collection.objects.link(cam)
    tgt = Vector((-35 if v not in ("dome",) and not v.startswith(("near", "tall")) else 0, 0, tz))
    cam.location = tgt + Vector((math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * d
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = 35; cam.data.clip_end = 2000
    sc.camera = cam; sc.render.filepath = f"{out}_{v}.png"; bpy.ops.render.render(write_still=True)
