import bpy
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, BoolProperty
from .utils import get_mmd_roots

class MMDHELPER_OT_OptimizePhysics(Operator):
    bl_idname = "mmdhelper.optimize_physics"
    bl_label = "高精度物理优化"
    bl_description = "提高 MMD 模型的物理解算精度"
    bl_options = {'REGISTER', 'UNDO'}

    substeps: IntProperty(name="子步数", default=10, min=1, max=50)
    solver_iterations: IntProperty(name="解算迭代", default=50, min=10, max=200)
    collision_margin: FloatProperty(name="碰撞边距", default=0.001, min=0.0, max=0.1, precision=4)

    def execute(self, context):
        roots = get_mmd_roots()
        if not roots:
            self.report({'WARNING'}, "场景中没有 MMD 模型")
            return {'CANCELLED'}

        scene = context.scene
        if not scene.rigidbody_world:
            bpy.ops.rigidbody.world_add()
        rw = scene.rigidbody_world
        rw.substeps_per_frame = self.substeps
        rw.solver_iterations = self.solver_iterations

        for root in roots:
            rig = getattr(root, 'mmd_rigid', None)
            if rig and hasattr(rig, 'groups'):
                for g in rig.groups:
                    g.collision_margin = self.collision_margin

        rw.point_cache.frame_start = scene.frame_start
        rw.point_cache.frame_end = scene.frame_end
        rw.point_cache.use_external = False
        rw.enabled = True

        self.report({'INFO'}, "物理参数已优化")
        return {'FINISHED'}


class MMDHELPER_OT_BakePhysics(Operator):
    bl_idname = "mmdhelper.bake_physics"
    bl_label = "烘焙物理到关键帧"
    bl_description = "将物理模拟结果烘焙为骨骼动画"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        roots = get_mmd_roots()
        if not roots:
            self.report({'WARNING'}, "无 MMD 模型")
            return {'CANCELLED'}

        scene = context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        if not scene.rigidbody_world:
            bpy.ops.rigidbody.world_add()
        scene.rigidbody_world.enabled = True

        for root in roots:
            arm = None
            for child in root.children:
                if child.type == 'ARMATURE':
                    arm = child
                    break
            if not arm:
                continue

            bpy.ops.object.select_all(action='DESELECT')
            arm.select_set(True)
            context.view_layer.objects.active = arm

            if arm.animation_data:
                arm.animation_data.action = None

            bpy.ops.nla.bake(
                frame_start=frame_start,
                frame_end=frame_end,
                only_selected=False,
                visual_keying=True,
                clear_constraints=False,
                use_current_action=True,
                bake_types={'POSE'}
            )

        self.report({'INFO'}, "物理烘焙完成")
        return {'FINISHED'}


class MMDHELPER_OT_AntiClip(Operator):
    bl_idname = "mmdhelper.anti_clip"
    bl_label = "防穿模强化"
    bl_description = "自动优化碰撞形状和碰撞组，减少穿透"
    bl_options = {'REGISTER', 'UNDO'}

    use_mesh_shape: BoolProperty(name="使用网格碰撞体", default=True)
    enable_self_collision: BoolProperty(name="布料自碰撞", default=True)

    def execute(self, context):
        roots = get_mmd_roots()
        if not roots:
            self.report({'WARNING'}, "未找到 MMD 模型")
            return {'CANCELLED'}

        if not context.scene.rigidbody_world:
            bpy.ops.rigidbody.world_add()
        context.scene.rigidbody_world.enabled = True

        for root in roots:
            rig = getattr(root, 'mmd_rigid', None)
            if not rig or not hasattr(rig, 'groups'):
                continue

            for group in rig.groups:
                rb_obj = getattr(group, 'rigid_body_object', None)
                if rb_obj is None and group.name in bpy.data.objects:
                    rb_obj = bpy.data.objects[group.name]
                if rb_obj and rb_obj.rigid_body and self.use_mesh_shape:
                    rb_obj.rigid_body.collision_shape = 'CONVEX_HULL'

                bone_name = group.name.lower()
                if 'hair' in bone_name or '髪' in bone_name:
                    group.collision_group = 1
                elif 'skirt' in bone_name or 'dress' in bone_name or 'スカート' in bone_name:
                    group.collision_group = 2
                else:
                    group.collision_group = 0

            if self.enable_self_collision:
                for arm in [c for c in root.children if c.type == 'ARMATURE']:
                    for mesh_obj in [c for c in arm.children if c.type == 'MESH']:
                        for mod in mesh_obj.modifiers:
                            if mod.type == 'CLOTH':
                                mod.settings.use_self_collision = True
                                mod.settings.self_collision_distance = 0.015

            if context.scene.rigidbody_world.substeps_per_frame < 10:
                context.scene.rigidbody_world.substeps_per_frame = 10
            if context.scene.rigidbody_world.solver_iterations < 50:
                context.scene.rigidbody_world.solver_iterations = 50

        self.report({'INFO'}, "防穿模设置完成")
        return {'FINISHED'}


classes = (
    MMDHELPER_OT_OptimizePhysics,
    MMDHELPER_OT_BakePhysics,
    MMDHELPER_OT_AntiClip,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
