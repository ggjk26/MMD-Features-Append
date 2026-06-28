import bpy
from mathutils import Vector


def meshes():
    return [o for o in bpy.data.objects if o.type == 'MESH']


def armatures():
    return [o for o in bpy.data.objects if o.type == 'ARMATURE']


def scene_bounds():
    min_v = Vector((1e10,1e10,1e10))
    max_v = Vector((-1e10,-1e10,-1e10))

    for obj in meshes():
        for v in obj.bound_box:
            w = obj.matrix_world @ Vector(v)
            min_v = Vector(map(min, min_v, w))
            max_v = Vector(map(max, max_v, w))

    return min_v, max_v


# =========================
# 🔥 关键修复：安全模式切换
# =========================
def safe_set_mode(mode="OBJECT", obj=None):

    if obj is None:
        obj = bpy.context.view_layer.objects.active

    if obj is None:
        objs = meshes()
        if not objs:
            return False
        obj = objs[0]

    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        bpy.ops.object.mode_set(mode=mode)
        return True
    except:
        return False
