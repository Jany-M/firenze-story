"""A reduced scan as a GLB of its own for the web (scenes that move a statue, e.g. the David leaving the Opera del Duomo).

Run:  blender -b --factory-startup --python blender/scripts/build_scan_glb.py -- <name> <height_m>
In:   blender/data/scans/<name>.npz (prep_scan.py)   Out: web/public/models/scans/<name>.glb
Real size in metres, base centred at the origin, the statue's front towards +Z in three.js (−Y in Blender), smooth normals,
one material "scan" (the app gives it its own). Licence as the source scan (blender/data/scans/README.md).
"""
import sys, os, bpy, numpy as np
name, H = sys.argv[sys.argv.index("--") + 1:][:2]; H = float(H)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = np.load(os.path.join(ROOT, "blender", "data", "scans", f"{name}.npz")); v = d["v"].astype(np.float64) * H; f = d["f"]
bpy.ops.wm.read_factory_settings(use_empty=True)
me = bpy.data.meshes.new(name); me.from_pydata(v.tolist(), [], f.tolist()); me.validate(); me.update()
for p in me.polygons: p.use_smooth = True
o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
me.materials.append(bpy.data.materials.new("scan"))
out = os.path.join(ROOT, "web", "public", "models", "scans", f"{name}.glb"); os.makedirs(os.path.dirname(out), exist_ok=True)
o.select_set(True); bpy.context.view_layer.objects.active = o
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_normals=True, export_image_format="NONE")
print("SCANGLB", name, len(f), "triangles", os.path.getsize(out), "bytes ->", out)
