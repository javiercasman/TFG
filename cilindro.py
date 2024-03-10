import bpy
import bmesh
from mathutils import Vector

armature = bpy.data.objects["armature"]

division_points = [0.0, 0.0797427652733119, 0.1517684887459807, 0.22379421221864954, 0.2958199356913183, 0.36784565916398715, 0.439871382636656, 0.5118971061093248, 0.5839228295819936, 0.6559485530546624, 0.7279742765273312, 0.8]

def view3d_find( return_area = False ):
    # returns first 3d view, normally we get from context
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    if return_area: return region, rv3d, v3d, area
                    return region, rv3d, v3d
    return None, None

if armature:
    #    bones = [armature.pose.bones[i] for i in range(0,6)]
    #    bbox = [armature.matrix_world @ armature.pose.bones[0].head]
    #    bbox += ([armature.matrix_world @ b.tail for b in bones])
    #    min_z = min(bbox, key=lambda v: v.z).z
    #    max_z = max(bbox, key=lambda v: v.z).z
        
    #    altura_cilindro = max_z - min_z
    offset = (armature.matrix_world @ armature.data.bones[0].head).z
    llama = bpy.data.objects["Llama"]
    altura_cilindro = llama.dimensions.z + 0.01
        
    #    radio_cilindro = 0.2
    radio_cilindro = max(llama.dimensions.x, llama.dimensions.y) / 2 + 0.05

    bpy.ops.mesh.primitive_cylinder_add(radius=radio_cilindro, depth=altura_cilindro)
        
    cilindro = bpy.context.active_object

    #    loc = armature.matrix_world @ armature.pose.bones[0].head
    #    loc.z += altura_cilindro/2
    loc = llama.location
    cilindro.location = loc
#
    """
    bpy.context.view_layer.objects.active = cilindro
    bpy.context.view_layer.update()
    
    bm = bmesh.new()
    
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = cilindro.data
    bm.from_mesh(mesh)
    bpy.ops.object.mode_set(mode='OBJECT')
        
    vertices = [v for v in bm.verts if v.co.z < 0.0]
    new_vertices = []
    for z in division_points:
        new_vertices.append([])
        for v in vertices:
            local_coords = v.co
            global_coords = cilindro.matrix_world @ local_coords
            global_coords.z = offset + z
            local_coords = cilindro.matrix_world.inverted() @ global_coords
            new_vert = bm.verts.new(local_coords)
            new_vertices[-1].append(new_vert)

    
    for e in new_vertices:
        for i in range(len(e)):
            if(i == len(e)-1): new_edge = bm.edges.new((e[i], e[0]))
            else: new_edge = bm.edges.new((e[i], e[i+1]))

    # Volver al modo de objeto y actualizar la malla
    bpy.ops.object.mode_set(mode='OBJECT')
    bm.to_mesh(mesh)
    bm.free()
    """
#

    bpy.context.view_layer.objects.active = armature
    
    armature.select_set(True)
    cilindro.select_set(True)

    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    armature.select_set(False)   
#    
    bpy.context.view_layer.objects.active = cilindro
    bpy.context.view_layer.update()
    
    bpy.ops.object.mode_set(mode='EDIT')
    region, rv3d, v3d, area = view3d_find(True)
    local_division_points=[]
    for z in division_points:
        value_z = z + offset         # Coordenada z global
        global_coords = Vector((0.0,0.0,value_z))
        local_coords = cilindro.matrix_world.inverted() @ global_coords
        local_division_points.append(local_coords.z)
    with bpy.context.temp_override(scene=bpy.context.scene, region=region, area=area, space=v3d):
        for i in range(len(local_division_points)):
            value = local_division_points[i]
            if i > 0: value -= local_division_points[i-1]
            value = -value + (1 - value) #Corregir
            bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":1, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, 
                                    "edge_index":2, "mesh_select_mode_init":(False, True, False)}, 
                                    TRANSFORM_OT_edge_slide={"value":value, "single_side":False, "use_even":False, "flipped":False, 
                                    "use_clamp":True, "mirror":True, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, 
                                    "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, 
                                    "use_snap_selectable":False, "snap_point":(0, 0, 0), "correct_uv":True, "release_confirm":True, 
                                    "use_accurate":False, "alt_navigation":False})
        # Borra cualquier selección existente

#
else:
    print("Armature no encontrado.") 