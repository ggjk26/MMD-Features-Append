import bpy
import os
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty
from .utils import get_all_mmd_meshes

class MMDHELPER_OT_ConvertPBR(Operator):
    bl_idname = "mmdhelper.convert_pbr"
    bl_label = "一键转换 PBR 材质（带法线）"
    bl_description = "将 MMD 卡通材质转为 Principled BSDF，自动关联法线贴图"
    bl_options = {'REGISTER', 'UNDO'}

    find_normal_auto: BoolProperty(name="自动查找法线贴图", default=True)
    normal_suffix: StringProperty(name="法线贴图后缀", default="_n")

    def execute(self, context):
        meshes = get_all_mmd_meshes()
        if not meshes:
            self.report({'WARNING'}, "无 MMD 模型网格")
            return {'CANCELLED'}

        converted = 0
        for mesh_obj in meshes:
            if mesh_obj.data.materials:
                for mat in mesh_obj.data.materials:
                    if mat and mat.node_tree:
                        if self._convert_material(mat, self.find_normal_auto, self.normal_suffix):
                            converted += 1

        self.report({'INFO'}, f"已转换 {converted} 个材质")
        return {'FINISHED'}

    def _convert_material(self, mat, auto_find_normal, normal_suffix):
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        if any(n.type == 'BSDF_PRINCIPLED' for n in nodes):
            return False

        tex_nodes = [n for n in nodes if n.type == 'TEX_IMAGE']
        if not tex_nodes:
            return False

        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (200, 300)
        bsdf.label = "MMD PBR"

        out = None
        for n in nodes:
            if n.type == 'OUTPUT_MATERIAL':
                out = n
                break
        if not out:
            out = nodes.new('ShaderNodeOutputMaterial')
            out.location = (600, 300)

        base_tex = tex_nodes[0]
        links.new(base_tex.outputs['Color'], bsdf.inputs['Base Color'])

        normal_tex = None
        if auto_find_normal and base_tex.image:
            base_path = bpy.path.abspath(base_tex.image.filepath)
            base_dir = os.path.dirname(base_path)
            base_name = os.path.splitext(os.path.basename(base_path))[0]
            clean_name = base_name
            for sfx in ['_d', '_c', '_base']:
                if clean_name.endswith(sfx):
                    clean_name = clean_name[:-len(sfx)]
                    break
            normal_name = clean_name + normal_suffix
            for ext in ['.png', '.jpg', '.tga', '.bmp']:
                candidate = os.path.join(base_dir, normal_name + ext)
                if os.path.exists(candidate):
                    img = bpy.data.images.load(candidate, check_existing=True)
                    normal_tex = nodes.new('ShaderNodeTexImage')
                    normal_tex.image = img
                    normal_tex.location = (200, 0)
                    normal_tex.label = "Normal"
                    normal_tex.image.colorspace_settings.name = 'Non-Color'
                    break

        if normal_tex:
            normal_map = nodes.new('ShaderNodeNormalMap')
            normal_map.location = (400, 0)
            links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])

        for link in list(out.inputs['Surface'].links):
            links.remove(link)
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

        return True


classes = (MMDHELPER_OT_ConvertPBR,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
