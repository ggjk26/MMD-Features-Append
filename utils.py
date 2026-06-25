import bpy

def mmd_tools_available():
    try:
        import mmd_tools
        return True
    except ImportError:
        return False

def get_mmd_roots():
    if not mmd_tools_available():
        return []
    roots = []
    for obj in bpy.data.objects:
        if hasattr(obj, 'mmd_type') and obj.mmd_type == 'ROOT':
            roots.append(obj)
    return roots

def get_all_mmd_meshes():
    meshes = []
    for root in get_mmd_roots():
        for arm in [c for c in root.children if c.type == 'ARMATURE']:
            meshes.extend([c for c in arm.children if c.type == 'MESH'])
    return meshes

def register():
    pass

def unregister():
    pass
