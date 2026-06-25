import bpy
from bpy.types import Panel
from bpy.props import FloatProperty, FloatVectorProperty, EnumProperty, BoolProperty
from .utils import mmd_tools_available, get_mmd_roots

class MMDHELPER_PT_Panel(Panel):
    bl_label = "MMD 助手"
    bl_idname = "MMDHELPER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MMD Helper"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if not mmd_tools_available():
            layout.label(text="需要先启用 mmd_tools 插件", icon='ERROR')
            return

        roots = get_mmd_roots()
        if roots:
            layout.label(text=f"已加载 {len(roots)} 个 MMD 模型")
        else:
            layout.label(text="未找到 MMD 模型", icon='INFO')
        layout.separator()

        # ---- 物理区 ----
        box = layout.box()
        box.label(text="物理优化", icon='PHYSICS')
        op = box.operator("mmdhelper.optimize_physics")
        op.substeps = 10
        op.solver_iterations = 50
        op.collision_margin = 0.001
        box.operator("mmdhelper.bake_physics")
        box.operator("mmdhelper.anti_clip")
        box.label(text="烘焙后可关闭刚体世界", icon='INFO')

        layout.separator()

        # ---- 材质区 ----
        box = layout.box()
        box.label(text="PBR 材质转换", icon='MATERIAL')
        op = box.operator("mmdhelper.convert_pbr")
        op.find_normal_auto = True
        op.normal_suffix = "_n"
        box.label(text="自动寻找法线贴图（与颜色贴图同目录）")

        layout.separator()

        # ---- 修复区 ----
        box = layout.box()
        box.label(text="模型诊断", icon='ERROR')
        box.operator("mmdhelper.repair_model")
        if not roots:
            box.label(text="若模型存在但未识别，请点击修复", icon='INFO')

        layout.separator()

        # ---- 摄像机构图区 ----
        box = layout.box()
        box.label(text="摄像机自动构图", icon='CAMERA_DATA')
        row = box.row(align=True)
        row.operator("mmdhelper.camera_fit", text="横版").mode = 'HORIZONTAL'
        row.operator("mmdhelper.camera_fit", text="竖版").mode = 'VERTICAL'
        row.operator("mmdhelper.camera_fit", text="1:1").mode = 'SQUARE'

        box.prop(scene, "mmdhelper_custom_ratio")
        op = box.operator("mmdhelper.camera_fit", text="自定义比例")
        op.mode = 'CUSTOM'
        op.custom_ratio = scene.mmdhelper_custom_ratio
        op.margin = scene.mmdhelper_margin
        box.prop(scene, "mmdhelper_margin")

        layout.separator()

        # ---- 布料转换区 ----
        box = layout.box()
        box.label(text="MMD 衣物转布料", icon='MOD_CLOTH')
        row = box.row(align=True)
        row.prop(scene, "mmdhelper_cloth_preset", text="")
        op = row.operator("mmdhelper.convert_cloth", text="转换")
        op.cloth_preset = scene.mmdhelper_cloth_preset
        op.use_selected_only = scene.mmdhelper_cloth_selected_only
        box.prop(scene, "mmdhelper_cloth_selected_only")

        layout.separator()

        # ---- 三渲二着色 ----
        box = layout.box()
        box.label(text="三渲二着色", icon='SHADING_RENDERED')
        row = box.row(align=True)
        row.prop(scene, "mmd_toon_preset", text="")
        op = row.operator("mmdhelper.apply_toon_shading", text="应用")
        op.use_selected_only = False
        op.fix_eye_white = scene.mmd_toon_fix_eye
        box.prop(scene, "mmd_toon_fix_eye")
        box.operator("mmdhelper.remove_toon_shading", text="移除")

        box.separator()
        col = box.column(align=True)
        col.prop(scene, "mmd_toon_shadow_threshold")
        col.prop(scene, "mmd_toon_shadow_color")
        col.prop(scene, "mmd_toon_shadow_layers")
        col.prop(scene, "mmd_toon_highlight_size")
        col.prop(scene, "mmd_toon_highlight_color")
        col.prop(scene, "mmd_toon_highlight_intensity")
        col.prop(scene, "mmd_toon_rim_strength")
        col.prop(scene, "mmd_toon_rim_color")
        col.prop(scene, "mmd_toon_ambient")
        col.prop(scene, "mmd_toon_emission")
        box.operator("mmdhelper.update_toon_params", text="应用参数")

        box.separator()
        box.label(text="轮廓线（描边）")
        op = box.operator("mmdhelper.auto_line_art", text="自动轮廓线")
        op.thickness = 30
        op.color = (0, 0, 0, 1)


def register():
    bpy.types.Scene.mmdhelper_custom_ratio = FloatVectorProperty(
        name="自定义宽高比", size=2, default=(16.0, 9.0), min=0.1, description="宽度 / 高度"
    )
    bpy.types.Scene.mmdhelper_margin = FloatProperty(
        name="边距 (%)", default=10, min=0, max=50, description="角色周围留白百分比"
    )
    bpy.types.Scene.mmdhelper_cloth_preset = EnumProperty(
        name="布料预设",
        items=[
            ('SILK', "丝绸", ""),
            ('COTTON', "棉布", ""),
            ('LEATHER', "皮革", ""),
            ('RUBBER', "橡胶", ""),
            ('DENIM', "牛仔布", ""),
        ],
        default='COTTON',
    )
    bpy.types.Scene.mmdhelper_cloth_selected_only = BoolProperty(
        name="仅选中的物体", default=False
    )

def unregister():
    del bpy.types.Scene.mmdhelper_custom_ratio
    del bpy.types.Scene.mmdhelper_margin
    del bpy.types.Scene.mmdhelper_cloth_preset
    del bpy.types.Scene.mmdhelper_cloth_selected_only
