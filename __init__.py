bl_info = {
    "name": "MMD Features Append",
    "author": "Your Name",
    "version": (3, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > MMFA",
    "description": "MMD 物理优化、PBR 转换、模型修复、摄像机构图、防穿模、布料转换、三渲二",
    "category": "Animation",
}

if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    importlib.reload(physics)
    importlib.reload(materials)
    importlib.reload(repair)
    importlib.reload(camera)
    importlib.reload(cloth)
    importlib.reload(toon_shading)
    importlib.reload(ui)
else:
    from . import utils
    from . import physics
    from . import materials
    from . import repair
    from . import camera
    from . import cloth
    from . import toon_shading
    from . import ui

import bpy

def register():
    utils.register()
    physics.register()
    materials.register()
    repair.register()
    camera.register()
    cloth.register()
    toon_shading.register()
    ui.register()

def unregister():
    utils.unregister()
    physics.unregister()
    materials.unregister()
    repair.unregister()
    camera.unregister()
    cloth.unregister()
    toon_shading.unregister()
    ui.unregister()

if __name__ == "__main__":
    register()
