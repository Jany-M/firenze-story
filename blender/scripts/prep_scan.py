"""Reduce a 3D-printing scan (STL) to a light mesh the landmark builds can place: blender/data/scans/<name>.npz.

Run:  blender -b --factory-startup --python blender/scripts/prep_scan.py -- <stl> <name> <triangles>
The stored mesh is normalised: feet (the lowest point) at z = 0, centred on the base, height 1, the statue's front towards -Y
(as Scan the World exports its figures), so landmark_scan.place() only scales, turns and moves it.
Sources and licences: docs/DATA-SOURCES.md (Scan the World); the reduced mesh keeps the source's licence (blender/data/scans/README.md).
"""
import sys, os, bpy, bmesh, numpy as np
argv = sys.argv[sys.argv.index("--") + 1:]
src, name, target = argv[0], argv[1], int(argv[2])
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=src)
o = bpy.context.selected_objects[0]; bpy.context.view_layer.objects.active = o
bm = bmesh.new(); bm.from_mesh(o.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)                     # print exports keep every triangle's own corners
bm.to_mesh(o.data); bm.free()
n0 = len(o.data.polygons)
m = o.modifiers.new("dec", "DECIMATE"); m.ratio = min(1.0, target / max(1, n0)); m.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier="dec")
me = o.data; me.calc_loop_triangles()
v = np.array([p.co[:] for p in me.vertices], dtype=np.float64)
f = np.array([t.vertices[:] for t in me.loop_triangles], dtype=np.int32)
lo = v[:, 2].min(); hi = v[:, 2].max(); H = hi - lo
foot = v[v[:, 2] < lo + 0.04 * H]                                          # the base: centre the statue on it
c = (foot[:, :2].min(0) + foot[:, :2].max(0)) / 2
v[:, :2] -= c; v[:, 2] -= lo; v /= H
out = os.path.join(ROOT, "blender", "data", "scans", f"{name}.npz")
np.savez_compressed(out, v=v.astype(np.float32), f=f, src_height=np.float32(H))
print("SCAN", name, "from", n0, "to", len(f), "triangles; height", round(H, 2), "source units; base", np.round(v[:, :2].min(0), 3), np.round(v[:, :2].max(0), 3), "->", out)
