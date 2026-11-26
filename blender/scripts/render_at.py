"""Preview renders around a given point (for models in absolute scene coordinates, e.g. san_lorenzo, medici_riccardi, mura):
blender -b blender/landmarks/<name>.blend --python blender/scripts/render_at.py -- <year> <out_prefix> <tx> <ty> <tz> <az:el:dist>[,<az:el:dist>…]
tx/ty are Blender X/Y (scene x / −scene z); az is degrees from +X (east), el degrees up."""
import bpy, math, sys
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
year = float(a[0]); out = a[1]; tgt = Vector((float(a[2]), float(a[3]), float(a[4])))
views = [tuple(float(x) for x in v.split(":")) for v in a[5].split(",")]
sc = bpy.context.scene
for o in bpy.data.objects:
    if "@" in o.name:
        f, t = o.name.split("@")[1].split(".")[0].split("-")
        o.hide_render = not (float(f) <= year < float(t))
w = bpy.data.worlds.new("sky"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.62, 0.72, 0.85, 1); bg.inputs[1].default_value = 0.9
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(200)); sun.data.energy = 3.5; sun.data.angle = 0.05
g = bpy.data.meshes.new("g"); c = tgt
g.from_pydata([(c.x - 500, c.y - 500, -0.05), (c.x + 500, c.y - 500, -0.05), (c.x + 500, c.y + 500, -0.05), (c.x - 500, c.y + 500, -0.05)], [], [(0, 1, 2, 3)])
go = bpy.data.objects.new("ground", g); sc.collection.objects.link(go)
gm = bpy.data.materials.new("ground"); gm.use_nodes = True; gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.42, 0.38, 0.33, 1); go.data.materials.append(gm)
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x = 1280; sc.render.resolution_y = 800
for i, (az, el, d) in enumerate(views):
    cam = bpy.data.objects.new(f"cam{i}", bpy.data.cameras.new(f"cam{i}")); sc.collection.objects.link(cam)
    cam.location = tgt + Vector((math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * d
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = 35; cam.data.clip_end = 3000
    sc.camera = cam; sc.render.filepath = f"{out}_{i}.png"; bpy.ops.render.render(write_still=True)
