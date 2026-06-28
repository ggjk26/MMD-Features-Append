import bpy
from mathutils import Vector
from .core import scene_bounds

def auto(context, mode="LANDSCAPE"):

    min_v, max_v = scene_bounds()
    center = (min_v + max_v) / 2
    size = max_v - min_v

    cam = bpy.data.objects.get("Camera")

    if not cam:
        bpy.ops.object.camera_add()
        cam = context.active_object

    dist = max(size.x, size.y, size.z) * 1.5

    if mode == "PORTRAIT":
        cam.location = center + Vector((0, -dist*0.9, size.z*0.2))
        context.scene.render.resolution_x = 1080
        context.scene.render.resolution_y = 1920

    elif mode == "LANDSCAPE":
        cam.location = center + Vector((0, -dist, size.z*0.3))
        context.scene.render.resolution_x = 1920
        context.scene.render.resolution_y = 1080

    elif mode == "CINEMATIC":
        cam.location = center + Vector((dist*0.2, -dist, size.z*0.4))
        context.scene.render.resolution_x = 2560
        context.scene.render.resolution_y = 1080

    cam.data.lens = 55

    direction = center - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    context.scene.camera = cam
