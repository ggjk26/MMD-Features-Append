bl_info = {
    "name": "MMD Features Append",
    "author": "Your Name",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > MMFA",
    "description": "MMD 物理优化、PBR 转换、模型修复、摄像机构图、防穿模、布料转换、三渲二",
    "category": "Animation",
}

import bpy

from .ui import PANEL_PT_main
from .ops import *

classes = [
    PANEL_PT_main,
    SCENE_OT_fix,
    MATERIAL_OT_pbr,
    CAMERA_OT_auto,
    EYE_OT_system,
    PHYSICS_OT_cloth,
    RENDER_OT_preset,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
