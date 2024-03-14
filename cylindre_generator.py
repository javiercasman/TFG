import bpy
import bmesh
from mathutils import Vector
import os

# division_points = [0.0, 0.0797427652733119, 0.1517684887459807, 0.22379421221864954, 0.2958199356913183, 0.36784565916398715, 0.439871382636656, 0.5118971061093248, 0.5839228295819936, 0.6559485530546624, 0.7279742765273312, 0.8]

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

def find_edge_loops(loop,max_loops=1000):
    i=0
    first_loop=loop
    while i<max_loops: 
        # Jump to adjacent face and walk two edges forward
        loop = loop.link_loop_next.link_loop_radial_next.link_loop_next
        loop.edge.select = True
        i += 1
        # If radial loop links back here, we're boundary, thus done        
        if loop == first_loop:
            break  

def generate_cylinder(flame_video_name):
    flame_name = flame_video_name.split('.')[0]
    directory =  bpy.path.abspath("//") + "flames" + ("//") + flame_name
    if not os.path.exists(directory):
        raise FileNotFoundError("No existen los archivos procesados del video \"" + flame_name +"\".\nPara solucionarlo, debe activar write_armature_file y/o write_cylinder_config_file")
    cfg_file_path = directory + ("//") + "Cylinder_" + flame_name + ".cfg"
    if not os.path.exists(cfg_file_path):
        raise FileNotFoundError("No existe ningun armature llamado \"" + armature_name + "\".\nPara generarlo, debe activar write_cylinder_config_file")
    
    armature_name = "Armature_" + flame_name
    if armature_name in bpy.context.scene.objects.keys():
        armature = bpy.data.objects[armature_name]
        bound_name = "Cylinder_" + flame_name
        if bound_name not in bpy.context.scene.objects.keys():
            offset = (armature.matrix_world @ armature.data.bones[0].head).z
            llama = bpy.data.objects["Llama"]
            altura_cilindro = llama.dimensions.z + 0.01

            radio_cilindro = max(llama.dimensions.x, llama.dimensions.y) / 2 + 0.05

            bpy.ops.mesh.primitive_cylinder_add(radius=radio_cilindro, depth=altura_cilindro)
            bpy.context.active_object.name = bound_name
                
            cilindro = bpy.context.active_object

            loc = llama.location
            cilindro.location = loc
            """
            # Bindear cilindro y armature
            bpy.ops.object.mode_set(mode='OBJECT') 
            bpy.context.view_layer.objects.active = armature
            
            armature.select_set(True)
            cilindro.select_set(True)

            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            bpy.ops.object.select_all(action='DESELECT')
            """
            # Bindear llama y cilindro
            mesh_def = llama.modifiers.new(name="MeshDeform", type='MESH_DEFORM')
            mesh_def.object = cilindro
            bpy.context.view_layer.objects.active = llama
            bpy.ops.object.meshdeform_bind(modifier='MeshDeform')
            bpy.ops.object.select_all(action='DESELECT')

            bpy.context.view_layer.objects.active = cilindro
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.context.view_layer.update()
            
            with open(cfg_file_path) as f:
                lines = f.readlines()            
            division_points = [float(x) for x in lines[0].split()]
            local_division_points=[]
            for z in division_points:
                value_z = z + offset         # Coordenada z global
                global_coords = Vector((0.0,0.0,value_z))
                local_coords = cilindro.matrix_world.inverted() @ global_coords
                local_division_points.append(local_coords.z+(altura_cilindro/2))

            region, rv3d, v3d, area = view3d_find(True)
            with bpy.context.temp_override(scene=bpy.context.scene, region=region, area=area, space=v3d):
                for idx, x in enumerate(local_division_points):
                    value = x
                    if idx > 0: 
                        value -= local_division_points[idx-1]
                        value = value / (1 - local_division_points[idx-1])
                    value = -value + (1 - value)
                    bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":1, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, 
                                            "edge_index":2, "mesh_select_mode_init":(False, True, False)}, 
                                            TRANSFORM_OT_edge_slide={"value":value, "single_side":False, "use_even":False, "flipped":False, 
                                            "use_clamp":True, "mirror":True, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, 
                                            "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, 
                                            "use_snap_selectable":False, "snap_point":(0, 0, 0), "correct_uv":True, "release_confirm":True, 
                                            "use_accurate":False, "alt_navigation":False})
            
            #bpy.ops.transform.resize(value=(1.44418, 1.44418, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', 
                    #                 constraint_axis=(True, True, False), mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=0.410684, 
                    #                 use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', 
                    #                 use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, alt_navigation=True)
            #bpy.ops.transform.resize(value=(2.11011, 2.11011, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', 
            #                         constraint_axis=(True, True, False), mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=0.410684, 
            #                         use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', 
            #                         use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, alt_navigation=True)

            bpy.ops.object.mode_set(mode='OBJECT') 
            bpy.context.view_layer.objects.active = armature
            
            armature.select_set(True)
            cilindro.select_set(True)

            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            bpy.ops.object.select_all(action='DESELECT')

            
        else:
            print("El bounding cylinder ya existe")
    else:
        print("Armature no encontrado.") 