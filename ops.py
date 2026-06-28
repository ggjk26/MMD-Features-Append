import bpy

from . import scene, material, camera, physics, eye, render


class SCENE_OT_fix(bpy.types.Operator):
    bl_idname = "scene.fix"
    bl_label = "Fix Scene"

    def execute(self, context):
        scene.fix()
        return {'FINISHED'}


class MATERIAL_OT_pbr(bpy.types.Operator):
    bl_idname = "material.pbr"
    bl_label = "PBR"

    def execute(self, context):
        material.pbr()
        return {'FINISHED'}


class CAMERA_OT_auto(bpy.types.Operator):
    bl_idname = "camera.auto"
    bl_label = "Camera"

    mode: bpy.props.StringProperty(default="LANDSCAPE")

    def execute(self, context):
        camera.auto(context, self.mode)
        return {'FINISHED'}


class PHYSICS_OT_cloth(bpy.types.Operator):
    bl_idname = "physics.cloth"
    bl_label = "Cloth"

    def execute(self, context):
        physics.cloth()
        return {'FINISHED'}


class EYE_OT_system(bpy.types.Operator):
    bl_idname = "eye.system"
    bl_label = "Eye"

    def execute(self, context):
        eye.system()
        return {'FINISHED'}


class RENDER_OT_preset(bpy.types.Operator):
    bl_idname = "render.preset"
    bl_label = "Preset"

    preset: bpy.props.StringProperty()

    def execute(self, context):
        render.preset(self.preset, context)
        return {'FINISHED'}
