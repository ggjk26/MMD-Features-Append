import bpy
from bpy.types import Operator
from .utils import get_mmd_roots

class MMDHELPER_OT_RepairModel(Operator):
    bl_idname = "mmdhelper.repair_model"
    bl_label = "修复识别错误"
    bl_description = "尝试修复 MMD 模型无法被正确识别的问题"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.data.objects:
            if hasattr(obj, 'mmd_type'):
                obj.update_tag()

        if not get_mmd_roots():
            armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
            if armatures:
                arm = armatures[0]
                if not (arm.parent and hasattr(arm.parent, 'mmd_type') and arm.parent.mmd_type == 'ROOT'):
                    root = bpy.data.objects.new("mmd_root", None)
                    context.collection.objects.link(root)
                    root.mmd_type = 'ROOT'
                    root.location = arm.location
                    if arm.parent:
                        arm.parent = root
                    else:
                        arm.parent = root
                    self.report({'INFO'}, "已创建缺失的 mmd_root")

        context.view_layer.update()
        context.scene.update()

        try:
            bpy.ops.mmd_tools.flush_cache()
        except:
            pass

        self.report({'INFO'}, "模型识别修复完成")
        return {'FINISHED'}


classes = (MMDHELPER_OT_RepairModel,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
