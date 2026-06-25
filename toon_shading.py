import bpy
from bpy.types import Operator
from bpy.props import (EnumProperty, FloatProperty, FloatVectorProperty,
                       BoolProperty, IntProperty)
from .utils import get_all_mmd_meshes

# 预设参数集（含游戏风格）
TOON_PRESETS = {
    'STANDARD': {
        'shadow_threshold': 0.5, 'shadow_color': (0.8, 0.75, 0.85, 1.0),
        'highlight_size': 0.1, 'highlight_color': (1.0, 1.0, 1.0, 1.0),
        'rim_strength': 0.2, 'rim_color': (1.0, 1.0, 1.0, 1.0),
        'ambient': 0.1, 'emission': 0.0, 'shadow_layers': 1, 'highlight_intensity': 0.5
    },
    'SOFT': {
        'shadow_threshold': 0.6, 'shadow_color': (0.85, 0.82, 0.9, 1.0),
        'highlight_size': 0.3, 'highlight_color': (1.0, 0.98, 0.96, 1.0),
        'rim_strength': 0.15, 'rim_color': (1.0, 1.0, 1.0, 1.0),
        'ambient': 0.2, 'emission': 0.0, 'shadow_layers': 2, 'highlight_intensity': 0.4
    },
    'SHARP': {
        'shadow_threshold': 0.4, 'shadow_color': (0.7, 0.65, 0.75, 1.0),
        'highlight_size': 0.05, 'highlight_color': (1.0, 1.0, 1.0, 1.0),
        'rim_strength': 0.4, 'rim_color': (1.0, 1.0, 1.0, 1.0),
        'ambient': 0.05, 'emission': 0.0, 'shadow_layers': 1, 'highlight_intensity': 0.8
    },
    'NO_SHADOW': {
        'shadow_threshold': 1.0, 'shadow_color': (1.0, 1.0, 1.0, 1.0),
        'highlight_size': 0.0, 'highlight_color': (0.0, 0.0, 0.0, 1.0),
        'rim_strength': 0.0, 'rim_color': (0.0, 0.0, 0.0, 1.0),
        'ambient': 1.0, 'emission': 1.0, 'shadow_layers': 0, 'highlight_intensity': 0.0
    },
    'WUTHERING_WAVES': {
        'shadow_threshold': 0.45, 'shadow_color': (0.6, 0.55, 0.75, 1.0),
        'highlight_size': 0.08, 'highlight_color': (0.9, 0.92, 1.0, 1.0),
        'rim_strength': 0.5, 'rim_color': (0.8, 0.85, 1.0, 1.0),
        'ambient': 0.08, 'emission': 0.05, 'shadow_layers': 1, 'highlight_intensity': 0.9
    },
    'STAR_RAIL': {
        'shadow_threshold': 0.55, 'shadow_color': (0.9, 0.85, 0.8, 1.0),
        'highlight_size': 0.15, 'highlight_color': (1.0, 0.98, 0.9, 1.0),
        'rim_strength': 0.25, 'rim_color': (1.0, 0.96, 0.88, 1.0),
        'ambient': 0.15, 'emission': 0.02, 'shadow_layers': 2, 'highlight_intensity': 0.5
    },
    'GENSHIN': {
        'shadow_threshold': 0.5, 'shadow_color': (0.78, 0.72, 0.85, 1.0),
        'highlight_size': 0.12, 'highlight_color': (1.0, 1.0, 0.95, 1.0),
        'rim_strength': 0.18, 'rim_color': (1.0, 1.0, 0.9, 1.0),
        'ambient': 0.12, 'emission': 0.01, 'shadow_layers': 1, 'highlight_intensity': 0.6
    },
    'ARKS': {
        'shadow_threshold': 0.4, 'shadow_color': (0.65, 0.62, 0.7, 1.0),
        'highlight_size': 0.06, 'highlight_color': (0.9, 0.9, 0.9, 1.0),
        'rim_strength': 0.45, 'rim_color': (0.7, 0.7, 0.8, 1.0),
        'ambient': 0.1, 'emission': 0.03, 'shadow_layers': 1, 'highlight_intensity': 0.7
    },
    'NIKKE': {
        'shadow_threshold': 0.7, 'shadow_color': (0.95, 0.9, 0.9, 1.0),
        'highlight_size': 0.2, 'highlight_color': (1.0, 0.95, 0.9, 1.0),
        'rim_strength': 0.3, 'rim_color': (1.0, 0.9, 0.85, 1.0),
        'ambient': 0.25, 'emission': 0.1, 'shadow_layers': 2, 'highlight_intensity': 0.8
    }
}

# 预设切换时同步场景属性
def update_toon_preset(self, context):
    preset = TOON_PRESETS.get(context.scene.mmd_toon_preset)
    if preset:
        scene = context.scene
        scene.mmd_toon_shadow_threshold = preset['shadow_threshold']
        scene.mmd_toon_shadow_color = preset['shadow_color']
        scene.mmd_toon_shadow_layers = preset['shadow_layers']
        scene.mmd_toon_highlight_size = preset['highlight_size']
        scene.mmd_toon_highlight_color = preset['highlight_color']
        scene.mmd_toon_highlight_intensity = preset['highlight_intensity']
        scene.mmd_toon_rim_strength = preset['rim_strength']
        scene.mmd_toon_rim_color = preset['rim_color']
        scene.mmd_toon_ambient = preset['ambient']
        scene.mmd_toon_emission = preset['emission']


class MMDHELPER_OT_ApplyToonShading(Operator):
    bl_idname = "mmdhelper.apply_toon_shading"
    bl_label = "应用三渲二着色器"
    bl_description = "为选中/所有 MMD 材质添加可定制的卡通节点组，可自动修复眼白发黑"
    bl_options = {'REGISTER', 'UNDO'}

    use_selected_only: BoolProperty(name="仅选中物体", default=False)
    fix_eye_white: BoolProperty(name="修复眼白发黑", default=True,
                                description="自动识别眼睛材质并设为自发光，避免阴影影响")

    def execute(self, context):
        if self.use_selected_only:
            target_meshes = [o for o in context.selected_objects if o.type == 'MESH']
            if not target_meshes:
                self.report({'WARNING'}, "请先选中至少一个网格物体")
                return {'CANCELLED'}
        else:
            target_meshes = get_all_mmd_meshes()
            if not target_meshes:
                self.report({'WARNING'}, "未找到 MMD 网格，请手动选择")
                return {'CANCELLED'}

        materials = set()
        for obj in target_meshes:
            for slot in obj.material_slots:
                if slot.material and slot.material.node_tree:
                    materials.add(slot.material)

        if not materials:
            self.report({'WARNING'}, "没有可处理的材质")
            return {'CANCELLED'}

        scene = context.scene
        params = {
            'shadow_threshold': scene.mmd_toon_shadow_threshold,
            'shadow_color': scene.mmd_toon_shadow_color,
            'highlight_size': scene.mmd_toon_highlight_size,
            'highlight_color': scene.mmd_toon_highlight_color,
            'highlight_intensity': scene.mmd_toon_highlight_intensity,
            'rim_strength': scene.mmd_toon_rim_strength,
            'rim_color': scene.mmd_toon_rim_color,
            'ambient': scene.mmd_toon_ambient,
            'emission': scene.mmd_toon_emission,
            'shadow_layers': scene.mmd_toon_shadow_layers,
        }

        for mat in materials:
            is_eye = self.fix_eye_white and self._is_eye_material(mat)
            self._apply_toon_nodes(mat, params, is_eye=is_eye)

        self.report({'INFO'}, f"已为 {len(materials)} 个材质应用三渲二")
        return {'FINISHED'}

    def _is_eye_material(self, mat):
        name = mat.name.lower()
        keywords = ['eye', '目', '瞳', 'white', '白眼', '眼球']
        return any(k in name for k in keywords)

    def _apply_toon_nodes(self, mat, params, is_eye=False):
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # 移除旧的三渲二节点组（包括普通和眼睛的）
        for old_name in ("MMD_Toon_Group", "MMD_Toon_Eye_Group"):
            old_group = nodes.get(old_name)
            if old_group:
                nodes.remove(old_group)

        out_node = nodes.get("Material Output")
        if not out_node:
            out_node = nodes.new('ShaderNodeOutputMaterial')
            out_node.location = (1000, 300)

        tex_nodes = [n for n in nodes if n.type == 'TEX_IMAGE']
        if tex_nodes:
            base_color = tex_nodes[0].outputs['Color']
        else:
            white = nodes.new('ShaderNodeRGB')
            white.outputs[0].default_value = (1, 1, 1, 1)
            white.location = (-200, 300)
            base_color = white.outputs['Color']

        group = nodes.new('ShaderNodeGroup')
        group.location = (400, 300)
        group.width = 220

        if is_eye:
            group.node_tree = self._build_eye_node_group()
            group.name = "MMD_Toon_Eye_Group"
            group.label = "MMD Eye Fix"
            links.new(base_color, group.inputs['Base Color'])
        else:
            group.node_tree = self._build_toon_node_group(params)
            group.name = "MMD_Toon_Group"
            group.label = "MMD Toon Shader"
            links.new(base_color, group.inputs['Base Color'])

            # 法线处理
            normal_socket = None
            for n in nodes:
                if n.type == 'TEX_IMAGE' and n.image and n.image.colorspace_settings.name == 'Non-Color':
                    normal_tex = n
                    normal_map = nodes.new('ShaderNodeNormalMap')
                    normal_map.location = (200, 100)
                    links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
                    normal_socket = normal_map.outputs['Normal']
                    break
            if not normal_socket:
                geom = nodes.new('ShaderNodeNewGeometry')
                geom.location = (200, 100)
                normal_socket = geom.outputs['Normal']
            links.new(normal_socket, group.inputs['Normal'])

        links.new(group.outputs['Shader'], out_node.inputs['Surface'])

    def _build_eye_node_group(self):
        """创建简单的自发光节点组，用于眼白修复"""
        group = bpy.data.node_groups.new("MMD_Toon_Eye_Group", 'ShaderNodeTree')
        group.interface.new_socket("Base Color", in_out='INPUT', socket_type='NodeSocketColor')
        group.interface.new_socket("Shader", in_out='OUTPUT', socket_type='NodeSocketShader')

        nodes = group.nodes
        links = group.links

        input_node = nodes.new('NodeGroupInput')
        input_node.location = (-200, 0)
        output_node = nodes.new('NodeGroupOutput')
        output_node.location = (200, 0)

        emission = nodes.new('ShaderNodeEmission')
        emission.location = (0, 0)
        emission.inputs['Strength'].default_value = 1.0

        links.new(input_node.outputs['Base Color'], emission.inputs['Color'])
        links.new(emission.outputs['Emission'], output_node.inputs['Shader'])
        return group

    def _build_toon_node_group(self, params):
        """构建卡通渲染节点组"""
        group = bpy.data.node_groups.new("MMD_Toon_Group", 'ShaderNodeTree')

        # 接口
        group.interface.new_socket("Base Color", in_out='INPUT', socket_type='NodeSocketColor')
        group.interface.new_socket("Normal", in_out='INPUT', socket_type='NodeSocketVector')
        group.interface.new_socket("Shadow Threshold", in_out='INPUT', socket_type='NodeSocketFloat')
        group.interface.new_socket("Shadow Color", in_out='INPUT', socket_type='NodeSocketColor')
        group.interface.new_socket("Highlight Size", in_out='INPUT', socket_type='NodeSocketFloat')
        group.interface.new_socket("Highlight Color", in_out='INPUT', socket_type='NodeSocketColor')
        group.interface.new_socket("Highlight Intensity", in_out='INPUT', socket_type='NodeSocketFloat')
        group.interface.new_socket("Rim Strength", in_out='INPUT', socket_type='NodeSocketFloat')
        group.interface.new_socket("Rim Color", in_out='INPUT', socket_type='NodeSocketColor')
        group.interface.new_socket("Ambient", in_out='INPUT', socket_type='NodeSocketFloat')
        group.interface.new_socket("Emission", in_out='INPUT', socket_type='NodeSocketFloat')
        group.interface.new_socket("Shader", in_out='OUTPUT', socket_type='NodeSocketShader')

        nodes = group.nodes
        links = group.links

        input_node = nodes.new('NodeGroupInput')
        input_node.location = (-800, 0)
        output_node = nodes.new('NodeGroupOutput')
        output_node.location = (800, 0)

        # ---- 漫反射 + 阴影 ----
        diffuse = nodes.new('ShaderNodeBsdfDiffuse')
        diffuse.location = (-400, 200)
        links.new(input_node.outputs['Base Color'], diffuse.inputs['Color'])
        links.new(input_node.outputs['Normal'], diffuse.inputs['Normal'])

        shader_to_rgb = nodes.new('ShaderNodeShaderToRGB')
        shader_to_rgb.location = (-200, 200)
        links.new(diffuse.outputs['BSDF'], shader_to_rgb.inputs['Shader'])

        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.location = (0, 200)
        ramp.color_ramp.interpolation = 'CONSTANT'
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
        ramp.color_ramp.elements[1].position = params['shadow_threshold']
        ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        links.new(shader_to_rgb.outputs['Color'], ramp.inputs['Fac'])

        mix_shadow = nodes.new('ShaderNodeMixRGB')
        mix_shadow.location = (200, 200)
        mix_shadow.blend_type = 'MIX'
        links.new(input_node.outputs['Base Color'], mix_shadow.inputs[1])
        links.new(input_node.outputs['Shadow Color'], mix_shadow.inputs[2])
        links.new(ramp.outputs['Color'], mix_shadow.inputs['Fac'])

        # ---- 高光 ----
        glossy = nodes.new('ShaderNodeBsdfGlossy')
        glossy.location = (-400, -100)
        glossy.distribution = 'GGX'
        links.new(input_node.outputs['Highlight Color'], glossy.inputs['Color'])
        rough_calc = nodes.new('ShaderNodeMath')
        rough_calc.location = (-600, -100)
        rough_calc.operation = 'SUBTRACT'
        rough_calc.inputs[0].default_value = 1.0
        links.new(input_node.outputs['Highlight Size'], rough_calc.inputs[1])
        links.new(rough_calc.outputs['Value'], glossy.inputs['Roughness'])

        glossy_rgb = nodes.new('ShaderNodeShaderToRGB')
        glossy_rgb.location = (-200, -100)
        links.new(glossy.outputs['BSDF'], glossy_rgb.inputs['Shader'])

        highlight_mix = nodes.new('ShaderNodeMixRGB')
        highlight_mix.location = (0, -100)
        highlight_mix.blend_type = 'MIX'
        highlight_mix.inputs[1].default_value = (0, 0, 0, 1)
        links.new(glossy_rgb.outputs['Color'], highlight_mix.inputs[2])
        links.new(input_node.outputs['Highlight Intensity'], highlight_mix.inputs['Fac'])

        # ---- 边缘光 ----
        fresnel = nodes.new('ShaderNodeLayerWeight')
        fresnel.location = (-400, -400)
        fresnel.blend = 0.5
        links.new(input_node.outputs['Normal'], fresnel.inputs['Normal'])
        rim_mix = nodes.new('ShaderNodeMixRGB')
        rim_mix.location = (-100, -400)
        rim_mix.blend_type = 'MIX'
        rim_mix.inputs[1].default_value = (0, 0, 0, 1)
        links.new(fresnel.outputs['Fresnel'], rim_mix.inputs['Fac'])
        links.new(input_node.outputs['Rim Color'], rim_mix.inputs[2])
        rim_strength_node = nodes.new('ShaderNodeMath')
        rim_strength_node.location = (100, -400)
        rim_strength_node.operation = 'MULTIPLY'
        links.new(rim_mix.outputs['Color'], rim_strength_node.inputs[0])
        links.new(input_node.outputs['Rim Strength'], rim_strength_node.inputs[1])

        # ---- 组合 ----
        emit_shadow = nodes.new('ShaderNodeEmission')
        emit_shadow.location = (300, 200)
        links.new(mix_shadow.outputs['Color'], emit_shadow.inputs['Color'])
        emit_shadow.inputs['Strength'].default_value = 1.0

        emit_highlight = nodes.new('ShaderNodeEmission')
        emit_highlight.location = (300, -100)
        links.new(highlight_mix.outputs['Color'], emit_highlight.inputs['Color'])
        emit_highlight.inputs['Strength'].default_value = 1.0

        emit_rim = nodes.new('ShaderNodeEmission')
        emit_rim.location = (300, -400)
        links.new(rim_strength_node.outputs['Value'], emit_rim.inputs['Strength'])
        links.new(input_node.outputs['Rim Color'], emit_rim.inputs['Color'])

        emit_ambient = nodes.new('ShaderNodeEmission')
        emit_ambient.location = (300, -600)
        links.new(input_node.outputs['Base Color'], emit_ambient.inputs['Color'])
        links.new(input_node.outputs['Ambient'], emit_ambient.inputs['Strength'])

        emit_emission = nodes.new('ShaderNodeEmission')
        emit_emission.location = (300, -800)
        links.new(input_node.outputs['Base Color'], emit_emission.inputs['Color'])
        links.new(input_node.outputs['Emission'], emit_emission.inputs['Strength'])

        add1 = nodes.new('ShaderNodeAddShader')
        add1.location = (500, 200)
        links.new(emit_shadow.outputs['Emission'], add1.inputs[0])
        links.new(emit_highlight.outputs['Emission'], add1.inputs[1])

        add2 = nodes.new('ShaderNodeAddShader')
        add2.location = (500, -100)
        links.new(add1.outputs['Shader'], add2.inputs[0])
        links.new(emit_rim.outputs['Emission'], add2.inputs[1])

        add3 = nodes.new('ShaderNodeAddShader')
        add3.location = (500, -300)
        links.new(add2.outputs['Shader'], add3.inputs[0])
        links.new(emit_ambient.outputs['Emission'], add3.inputs[1])

        add4 = nodes.new('ShaderNodeAddShader')
        add4.location = (500, -500)
        links.new(add3.outputs['Shader'], add4.inputs[0])
        links.new(emit_emission.outputs['Emission'], add4.inputs[1])

        links.new(add4.outputs['Shader'], output_node.inputs['Shader'])

        # 写入默认参数
        for input_socket in group.interface.items_tree:
            name = input_socket.name
            if name == 'Shadow Threshold':
                input_socket.default_value = params['shadow_threshold']
            elif name == 'Shadow Color':
                input_socket.default_value = params['shadow_color']
            elif name == 'Highlight Size':
                input_socket.default_value = params['highlight_size']
            elif name == 'Highlight Color':
                input_socket.default_value = params['highlight_color']
            elif name == 'Highlight Intensity':
                input_socket.default_value = params['highlight_intensity']
            elif name == 'Rim Strength':
                input_socket.default_value = params['rim_strength']
            elif name == 'Rim Color':
                input_socket.default_value = params['rim_color']
            elif name == 'Ambient':
                input_socket.default_value = params['ambient']
            elif name == 'Emission':
                input_socket.default_value = params['emission']

        return group


class MMDHELPER_OT_RemoveToonShading(Operator):
    bl_idname = "mmdhelper.remove_toon_shading"
    bl_label = "移除三渲二着色器"
    bl_description = "从所有材质中删除三渲二节点组（含眼睛修复）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        count = 0
        for mat in bpy.data.materials:
            if mat.node_tree:
                for node_name in ("MMD_Toon_Group", "MMD_Toon_Eye_Group"):
                    ng = mat.node_tree.nodes.get(node_name)
                    if ng:
                        mat.node_tree.nodes.remove(ng)
                        count += 1
        self.report({'INFO'}, f"已从 {count} 个材质移除三渲二")
        return {'FINISHED'}


class MMDHELPER_OT_UpdateToonParams(Operator):
    bl_idname = "mmdhelper.update_toon_params"
    bl_label = "应用三渲二参数"
    bl_description = "将当前面板参数推送到所有普通三渲二材质（不修改眼睛材质）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        params = {
            'shadow_threshold': scene.mmd_toon_shadow_threshold,
            'shadow_color': scene.mmd_toon_shadow_color,
            'highlight_size': scene.mmd_toon_highlight_size,
            'highlight_color': scene.mmd_toon_highlight_color,
            'highlight_intensity': scene.mmd_toon_highlight_intensity,
            'rim_strength': scene.mmd_toon_rim_strength,
            'rim_color': scene.mmd_toon_rim_color,
            'ambient': scene.mmd_toon_ambient,
            'emission': scene.mmd_toon_emission,
        }
        updated = 0
        for mat in bpy.data.materials:
            if mat.node_tree:
                group_node = mat.node_tree.nodes.get("MMD_Toon_Group")
                if group_node and group_node.node_tree:
                    for key, value in params.items():
                        socket_name = key.replace('_', ' ').title()
                        if socket_name in group_node.inputs:
                            group_node.inputs[socket_name].default_value = value
                    # 更新内部 ColorRamp
                    for node in group_node.node_tree.nodes:
                        if node.type == 'VALTORGB':
                            node.color_ramp.elements[1].position = params['shadow_threshold']
                    updated += 1
        self.report({'INFO'}, f"已更新 {updated} 个材质的参数")
        return {'FINISHED'}


class MMDHELPER_OT_AutoLineArt(Operator):
    bl_idname = "mmdhelper.auto_line_art"
    bl_label = "自动轮廓线"
    bl_description = "为选中的网格添加 Line Art 修改器（Grease Pencil 描边）"
    bl_options = {'REGISTER', 'UNDO'}

    thickness: IntProperty(name="线条粗细", default=30, min=1, max=500)
    color: FloatVectorProperty(name="线条颜色", subtype='COLOR', default=(0, 0, 0, 1), size=4, min=0, max=1)

    def execute(self, context):
        target_meshes = [o for o in context.selected_objects if o.type == 'MESH']
        if not target_meshes:
            target_meshes = get_all_mmd_meshes()
        if not target_meshes:
            self.report({'WARNING'}, "无可用网格")
            return {'CANCELLED'}

        gp_obj = bpy.data.objects.get("MMD_LineArt")
        if not gp_obj:
            gp_data = bpy.data.grease_pencils.new("MMD_LineArt")
            gp_obj = bpy.data.objects.new("MMD_LineArt", gp_data)
            context.collection.objects.link(gp_obj)
            gp_obj.show_in_front = True

        gp_mod = None
        for mod in gp_obj.grease_pencil_modifiers:
            if mod.type == 'LINE_ART':
                gp_mod = mod
                break
        if not gp_mod:
            gp_mod = gp_obj.grease_pencil_modifiers.new("LineArt", 'LINE_ART')

        gp_mod.thickness = self.thickness
        mat_name = "MMD_LineArt_Material"
        if mat_name not in bpy.data.materials:
            mat = bpy.data.materials.new(mat_name)
            mat.use_nodes = True
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*self.color[:3], 1)
        gp_obj.data.materials.clear()
        gp_obj.data.materials.append(bpy.data.materials[mat_name])
        gp_mod.target_material = bpy.data.materials[mat_name]

        if not gp_mod.source_collection:
            collection = bpy.data.collections.new("LineArt_Source")
            context.scene.collection.children.link(collection)
            gp_mod.source_collection = collection
        else:
            for obj in gp_mod.source_collection.objects:
                gp_mod.source_collection.objects.unlink(obj)

        for obj in target_meshes:
            gp_mod.source_collection.objects.link(obj)

        self.report({'INFO'}, f"已为 {len(target_meshes)} 个物体添加轮廓线")
        return {'FINISHED'}


classes = (
    MMDHELPER_OT_ApplyToonShading,
    MMDHELPER_OT_RemoveToonShading,
    MMDHELPER_OT_UpdateToonParams,
    MMDHELPER_OT_AutoLineArt,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.mmd_toon_preset = EnumProperty(
        name="预设",
        items=[
            ('STANDARD', "标准", ""),
            ('SOFT', "柔和", ""),
            ('SHARP', "锐利", ""),
            ('NO_SHADOW', "无阴影", ""),
            ('WUTHERING_WAVES', "鸣潮", ""),
            ('STAR_RAIL', "崩坏：星穹铁道", ""),
            ('GENSHIN', "原神", ""),
            ('ARKS', "明日方舟", ""),
            ('NIKKE', "胜利女神：妮姬", ""),
        ],
        default='STANDARD',
        update=update_toon_preset
    )
    bpy.types.Scene.mmd_toon_fix_eye = BoolProperty(name="修复眼白", default=True)
    bpy.types.Scene.mmd_toon_shadow_threshold = FloatProperty(name="阴影阈值", default=0.5, min=0.0, max=1.0)
    bpy.types.Scene.mmd_toon_shadow_color = FloatVectorProperty(name="阴影颜色", subtype='COLOR', default=(0.8, 0.75, 0.85, 1), size=4, min=0, max=1)
    bpy.types.Scene.mmd_toon_shadow_layers = IntProperty(name="阴影层数", default=1, min=0, max=3)
    bpy.types.Scene.mmd_toon_highlight_size = FloatProperty(name="高光尺寸", default=0.1, min=0, max=1)
    bpy.types.Scene.mmd_toon_highlight_color = FloatVectorProperty(name="高光颜色", subtype='COLOR', default=(1, 1, 1, 1), size=4, min=0, max=1)
    bpy.types.Scene.mmd_toon_highlight_intensity = FloatProperty(name="高光强度", default=0.5, min=0, max=1)
    bpy.types.Scene.mmd_toon_rim_strength = FloatProperty(name="边缘光强度", default=0.2, min=0, max=1)
    bpy.types.Scene.mmd_toon_rim_color = FloatVectorProperty(name="边缘光颜色", subtype='COLOR', default=(1, 1, 1, 1), size=4, min=0, max=1)
    bpy.types.Scene.mmd_toon_ambient = FloatProperty(name="环境光", default=0.1, min=0, max=1)
    bpy.types.Scene.mmd_toon_emission = FloatProperty(name="自发光", default=0.0, min=0, max=1)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mmd_toon_preset
    del bpy.types.Scene.mmd_toon_fix_eye
    del bpy.types.Scene.mmd_toon_shadow_threshold
    del bpy.types.Scene.mmd_toon_shadow_color
    del bpy.types.Scene.mmd_toon_shadow_layers
    del bpy.types.Scene.mmd_toon_highlight_size
    del bpy.types.Scene.mmd_toon_highlight_color
    del bpy.types.Scene.mmd_toon_highlight_intensity
    del bpy.types.Scene.mmd_toon_rim_strength
    del bpy.types.Scene.mmd_toon_rim_color
    del bpy.types.Scene.mmd_toon_ambient
    del bpy.types.Scene.mmd_toon_emission
