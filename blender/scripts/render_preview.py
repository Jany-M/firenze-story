import bpy, math
from mathutils import Vector
scn = bpy.context.scene
x = 0.0
for c in bpy.data.collections:
    objs = list(c.objects)
    w = max(max((o.matrix_world @ Vector(v)).x for v in o.bound_box) for o in objs) - min(min((o.matrix_world @ Vector(v)).x for v in o.bound_box) for o in objs)
    for o in objs: o.location.x += x + w/2
    x += w + 0.6
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam)
cam.location = (x/2, -x*0.95, 6.5); cam.rotation_euler = (math.radians(84), 0, 0); cam.data.lens = 40; scn.camera = cam
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 4; sun.rotation_euler = (0.8, 0.3, 0.6); scn.collection.objects.link(sun)
w = bpy.data.worlds.new("w"); scn.world = w; w.color = (0.9, 0.9, 0.92)
bpy.ops.mesh.primitive_plane_add(size=200)
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 1600; scn.render.resolution_y = 560
scn.render.filepath = r"E:\Dropbox\_PROJECTS_\CODE\firenze-story\blender\renders\asset_library.png"
bpy.ops.render.render(write_still=True)
result = {"collections": len(bpy.data.collections), "width_m": round(x,1)}
