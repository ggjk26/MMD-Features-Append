import bpy

def pbr():

    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue

        for mat in obj.data.materials:
            if not mat:
                continue

            mat.use_nodes = True

            nodes = mat.node_tree.nodes
            if any(n.type == 'BSDF_PRINCIPLED' for n in nodes):
                continue
