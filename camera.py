import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, FloatVectorProperty, FloatProperty
from .utils import get_all_mmd_meshes
from mathutils import Vector

class MMDHELPER_OT_CameraFit(Operator):
    bl_idname = "mmdhelper.camera_fit"
    bl_label = "自动构图"
    bl_description = "将摄像机对准模型，使其完整出现在画面中"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        name="构图模式",
        items=[
            ('HORIZONTAL', "横版 16:9", ""),
            ('VERTICAL', "竖版 9:16", ""),
            ('SQUARE', "正方形 1:1", ""),
            ('CUSTOM', "自定义比例", ""),
        ],
        default='HORIZONTAL',
    )
    custom_ratio: FloatVectorProperty(name="自定义宽高比", size=2, default=(16.0, 9.0), min=0.1)
    margin: FloatProperty(name="边距 (%)", default=10, min=0, max=50)

    def execute(self, context):
        scene = context.scene
        cam = scene.camera
        if not cam:
            self.report({'ERROR'}, "场景没有活动摄像机")
            return {'CANCELLED'}

        target_objects = []
        if context.selected_objects:
            target_objects = [o for o in context.selected_objects if o.type == 'MESH']
        if not target_objects:
            target_objects = get_all_mmd_meshes()
        if not target_objects:
            self.report({'ERROR'}, "未找到可用的网格模型")
            return {'CANCELLED'}

        bbox_corners = []
        for obj in target_objects:
            for corner in obj.bound_box:
                world_corner = obj.matrix_world @ Vector(corner)
                bbox_corners.append(world_corner)
        if not bbox_corners:
            return {'CANCELLED'}

        min_vec = Vector(bbox_corners[0])
        max_vec = Vector(bbox_corners[0])
        for v in bbox_corners:
            min_vec.x = min(min_vec.x, v.x)
            min_vec.y = min(min_vec.y, v.y)
            min_vec.z = min(min_vec.z, v.z)
            max_vec.x = max(max_vec.x, v.x)
            max_vec.y = max(max_vec.y, v.y)
            max_vec.z = max(max_vec.z, v.z)

        center = (min_vec + max_vec) / 2

        if self.mode == 'HORIZONTAL':
            ratio = 16.0 / 9.0
        elif self.mode == 'VERTICAL':
            ratio = 9.0 / 16.0
        elif self.mode == 'SQUARE':
            ratio = 1.0
        else:
            ratio = self.custom_ratio[0] / self.custom_ratio[1]

        sensor_width = cam.data.sensor_width
        if cam.data.sensor_fit != 'VERTICAL':
            effective_sensor_height = sensor_width / ratio
        else:
            effective_sensor_height = cam.data.sensor_height
        focal = cam.data.lens

        old_loc = cam.location.copy()
        old_rot = cam.rotation_euler.copy()
        cam.location = center + Vector((0.0, 0.0, 10.0))
        direction = center - cam.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam.rotation_euler = rot_quat.to_euler()

        cam_matrix = cam.matrix_world.inverted()
        projected = []
        for v in bbox_corners:
            local_v = cam_matrix @ v
            if local_v.z == 0:
                continue
            x = local_v.x / (-local_v.z)
            y = local_v.y / (-local_v.z)
            projected.append((x, y))

        if not projected:
            cam.location = old_loc
            cam.rotation_euler = old_rot
            self.report({'ERROR'}, "无法计算投影")
            return {'CANCELLED'}

        min_x = min(p[0] for p in projected)
        max_x = max(p[0] for p in projected)
        min_y = min(p[1] for p in projected)
        max_y = max(p[1] for p in projected)
        height_proj = max_y - min_y

        current_dist = (cam.location - center).length
        H_real = height_proj * current_dist

        margin_factor = 1.0 + (self.margin / 100.0)
        target_ratio = 1.0 / margin_factor
        new_dist = (H_real * focal) / (effective_sensor_height * target_ratio)

        cam_vec = (cam.location - center).normalized()
        new_location = center - cam_vec * new_dist
        cam.location = new_location

        direction = center - cam.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam.rotation_euler = rot_quat.to_euler()

        self.report({'INFO'}, f"摄像机已调整至距离 {new_dist:.2f}")
        return {'FINISHED'}


classes = (MMDHELPER_OT_CameraFit,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
