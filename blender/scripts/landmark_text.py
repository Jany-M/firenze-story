"""Real lettering for landmark models: inscriptions on friezes and attics (Blender's default typeface)."""
import bpy
from landmark_kit import bm_for

def lettering(part, mat, Fr, uc, v, n, text, size, width=None, depth=0.03):
    """A Blender text object turned to a mesh and laid on the face of frame Fr: centred on uc, baseline at v, standing out
    from n by depth, reading left to right for someone facing the wall. Scaled down to fit `width` when given."""
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = text; cu.size = size; cu.align_x = "CENTER"; cu.extrude = depth / 2
    ob = bpy.data.objects.new("txt", cu); bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get(); eo = ob.evaluated_get(dg); me = eo.to_mesh()
    xs = [w.co.x for w in me.vertices]; k = 1.0
    if width and xs and max(xs) - min(xs) > width: k = width / (max(xs) - min(xs))
    # reading direction: left to right for someone facing the wall, i.e. along up × n; flip x (and the winding) when F.u runs the other way
    sx = 1.0 if Fr.v.cross(Fr.n).dot(Fr.u) > 0 else -1.0
    bm = bm_for(part, mat); vm = {}
    for w in me.vertices: vm[w.index] = bm.verts.new(Fr.p(uc + sx * w.co.x * k, v + w.co.y * k, n + depth / 2 + w.co.z))
    for f in me.polygons:
        try: bm.faces.new([vm[i] for i in (f.vertices if sx > 0 else list(f.vertices)[::-1])])
        except ValueError: pass
    eo.to_mesh_clear(); bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
