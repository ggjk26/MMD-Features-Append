import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty
from .utils import get_mmd_roots

class MMDHELPER_OT_ConvertCloth(Operator):
    bl_idname = "mmdhelper.convert_cloth"
    bl_label = "一键布料转换"
    bl_description = "将 MMD 衣物网格转换为 Blender 布料模拟，按预设设置物理参数"
    bl_options = {'REGISTER', 'UNDO'}

    cloth_preset: EnumProperty(
        name="布料预设",
        items=[
            ('SILK', "丝绸", "轻薄柔软，适合丝带、薄裙"),
            ('COTTON', "棉布", "常规布料，适合日常服装"),
            ('LEATHER', "皮革", "厚重僵硬，适合皮带、盔甲"),
            ('RUBBER', "橡胶", "高弹性，适合紧身衣"),
            ('DENIM', "牛仔布", "厚重较硬，适合裤子、外套"),
        ],
        default='COTTON',
    )
    use_selected_only: BoolProperty(name="仅选中物体", default=False)

    def execute(self, context):
        if self.use_selected_only:
            target_meshes = [o for o in context.selected_objects if o.type == 'MESH']
            if not target_meshes:
                self.report({'WARNING'}, "请选中至少一个网格物体")
                return {'CANCELLED'}
        else:
            target_meshes = self._find_cloth_meshes()
            if not target_meshes:
                self.report({'WARNING'}, "未找到衣物网格，请手动选择")
                return {'CANCELLED'}

        presets = {
            'SILK':    (0.150, 0.5, 5.0, 5.0, 5.0, 0.5),
            'COTTON':  (0.300, 1.0, 15.0, 15.0, 5.0, 2.5),
            'LEATHER': (0.600, 1.5, 50.0, 50.0, 20.0, 10.0),
            'RUBBER':  (0.400, 0.8, 30.0, 30.0, 10.0, 1.0),
            'DENIM':   (0.500, 1.2, 40.0, 40.0, 15.0, 8.0),
        }
        mass, air, tension, compression, shear, bend = presets[self.cloth_preset]

        for obj in target_meshes:
            cloth_mod = None
            for mod in obj.modifiers:
                if mod.type == 'CLOTH':
                    cloth_mod = mod
                    break
            if not cloth_mod:
                cloth_mod = obj.modifiers.new(name="Cloth", type='CLOTH')

            settings = cloth_mod.settings
            settings.use_self_collision = True
            settings.self_collision_distance = 0.015
            settings.collision_distance = 0.015
            settings.mass = mass
            settings.air_damping = air
            settings.tension_stiffness = tension
            settings.compression_stiffness = compression
            settings.shear_stiffness = shear
            settings.bending_stiffness = bend
            settings.quality = 5

            if not cloth_mod.settings.vertex_group_mass:
                for vg in obj.vertex_groups:
                    if 'cloth' in vg.name.lower() or 'skirt' in vg.name.lower():
                        cloth_mod.settings.vertex_group_mass = vg.name
                        break

        self.report({'INFO'}, f"已将 {len(target_meshes)} 个网格转换为 {self.cloth_preset} 布料")
        return {'FINISHED'}

    def _find_cloth_meshes(self):
        candidates = []
        keywords = ['skirt', 'dress', 'スカート', 'cloth', '衣服', '裙', '上衣', 'パンツ']
        for root in get_mmd_roots():
            for arm in [c for c in root.children if c.type == 'ARMATURE']:
                for mesh_obj in [c for c in arm.children if c.type == 'MESH']:
                    name_lower = mesh_obj.name.lower()
                    if any(kw in name_lower for kw in keywords):
                        candidates.append(mesh_obj)
        return candidates


classes = (MMDHELPER_OT_ConvertCloth,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
