import bpy

def system():

    for obj in bpy.data.objects:

        if obj.type != 'MESH':
            continue

        for mat in obj.data.materials:
            if not mat:
                continue

            if "eye" not in mat.name.lower():
                continue

            mat.use_nodes = True

            for n in mat.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED':
                    n.inputs["Roughness"].default_value = 0.25
                    n.inputs["Metallic"].default_value = 0.0
