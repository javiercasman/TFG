import bpy
from mathutils import Vector
import os

bpy.ops.preferences.addon_enable(module="animation_animall")
escala = 1 #en el 2 no queda muy bien, lo dejamos en 1 y si vemos que no convence lo quitamos y ya

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

def animation_setup(flame_video_name, collection_name):
    flame_name = flame_video_name.split('.')[0]
    # dir = (os.path.abspath(os.path.join(bpy.path.abspath("//"), os.pardir)))
    # dir = (os.path.abspath(os.path.join(dir, os.pardir))) #//TFG
    dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) 
    _, r, w = collection_name.split('_')
    directory =  dir + ("//") + "flames" + ("//") + flame_name + ("//") + r + ("_") + w
    if not os.path.exists(directory):
        raise FileNotFoundError("No existen los archivos procesados del video \"" + flame_name +"\".\n")
    cfg_file_path = directory + ("//") + "Config_" + flame_name + ".cfg"
    if not os.path.exists(cfg_file_path):
        raise FileNotFoundError("No existe ningun archivo de configuracion llamado \"" + "Config_" + flame_name + ".cfg" + "\".\n")
    
    armature_name = "Armature_" + collection_name
    if armature_name in bpy.context.scene.objects.keys():
        armature = bpy.data.objects[armature_name]
        bound_name = "Cylinder_" + collection_name
        if bound_name not in bpy.context.scene.objects.keys():
            if bpy.context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
        
            llama = bpy.data.objects["Llama_" + collection_name]
            altura_cilindro = llama.dimensions.z + 0.01
            radio_cilindro = max(llama.dimensions.x, llama.dimensions.y) / 2 + 0.05
            
            bpy.ops.mesh.primitive_cylinder_add(radius=radio_cilindro, depth=altura_cilindro)
            bpy.context.active_object.name = bound_name
                
            cilindro = bpy.context.active_object

            loc = llama.location
            cilindro.location = loc

            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = cilindro
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.context.view_layer.update()

            offset = (armature.matrix_world @ armature.data.bones[0].head).z
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
            verts = []
            # edges = []
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
                                            "use_accurate":False})
                                            
                    bpy.ops.object.mode_set(mode='OBJECT') # Para que se actualice el número de vertices y edges
                    
                    selected_verts = [v.index for v in cilindro.data.vertices if v.select]
                    #selected_edges = [e.index for e in cilindro.data.edges if e.select]

                    verts.append(selected_verts)
                    #edges.append(selected_edges)
                    bpy.ops.object.mode_set(mode='EDIT') 

            #seleccionar edges y verts
            #bpy.ops.object.mode_set(mode='OBJECT') 
            #for edge in cilindro.data.edges:
            #    edge.select = False
            #for vertex in cilindro.data.vertices:
            #    vertex.select = False
            #bpy.ops.object.mode_set(mode='EDIT')

            bpy.ops.mesh.select_all(action='DESELECT') #para deseleccionar todos los edges y verts
            
            initial_vertex_locations = [v.co.copy() for v in cilindro.data.vertices]
            cilindro.select_set(True)#innecesario?
            bpy.ops.object.mode_set(mode='OBJECT') 

            n_frames = len(lines)-2

            if bpy.context.scene.frame_end < n_frames:
                bpy.context.scene.frame_end = n_frames

            for frame in range(n_frames):
                width_frame = []
                bpy.context.scene.frame_set(frame)
                bpy.context.scene.animall_properties.key_point_location = True
                bpy.context.scene.animall_properties.key_selected = True
                if frame > 0:
                    bpy.ops.object.mode_set(mode='OBJECT') 
                    for v, loc in zip(cilindro.data.vertices, initial_vertex_locations):
                        v.select = True
                        v.co = loc #Para que funcione esto tiene que estar en object mode
                    #bpy.ops.anim.insert_keyframe_animall()

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT') #para deseleccionar todos los edges y verts
                bpy.ops.object.mode_set(mode='OBJECT')
                widths = lines[frame+1].split()
                for i in range(0, len(widths), 2):
                    izq, der = float(widths[i]) * escala, float(widths[i+1]) * escala
                    w = [izq,der]
                    width_frame.append(w)
                for idx, x in enumerate(width_frame):
                    w_left = x[0]
                    w_right = x[1]
                    verts_loopcut = verts[idx]

                    for vert in verts_loopcut:
                        cilindro.data.vertices[vert].select = True
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.hide(unselected=True)
                    bpy.ops.mesh.select_all(action='DESELECT') #para deseleccionar todos los edges y verts

                    if w_left > w_right:
                        left_radio = radio_cilindro + w_left
                        resize_scale = left_radio / radio_cilindro
                        
                        bpy.ops.object.mode_set(mode='OBJECT')
                        for vert in verts_loopcut:
                            cilindro.data.vertices[vert].select = True #Solo funciona en object mode
                        bpy.ops.object.mode_set(mode='EDIT')                       
                        
                        bpy.ops.transform.resize(value=(resize_scale, resize_scale, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.8, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.mode_set(mode='EDIT')
                        
                        bpy.ops.mesh.select_all(action='DESELECT') #para deseleccionar todos los edges y verts

                        bpy.ops.object.mode_set(mode='OBJECT')

                        left_extr_vert = cilindro.data.vertices[verts_loopcut[8]]
                        right_extr_vert = cilindro.data.vertices[verts_loopcut[24]]

                        right_co = cilindro.matrix_world @ right_extr_vert.co
                        left_co = cilindro.matrix_world @ left_extr_vert.co

                        prop_size = (right_co - left_co).length

                        move_dist = w_left - w_right

                        right_extr_vert.select = True

                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.transform.translate(value=(move_dist, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=prop_size, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

                        # median_point = Vector()
                        # bpy.ops.object.mode_set(mode='OBJECT')
                        # for vert in verts_loopcut_right:
                        #     cilindro.data.vertices[vert].select = True
                        #     median_point += cilindro.matrix_world @ cilindro.data.vertices[vert].co
                            
                        # cilindro.data.vertices[verts_loopcut_left[0]].select = True #ahora es una medialuna, mas facil
                        # median_point += cilindro.matrix_world  @ cilindro.data.vertices[verts_loopcut_left[0]].co
                        # median_point /= (len(verts_loopcut_right) + 1)
                        
                        # left_extreme_vertice = cilindro.matrix_world  @ cilindro.data.vertices[verts_loopcut_left[8]].co
                        # prop_size = (median_point - left_extreme_vertice).length
                        
                        # right_extreme_vertice = cilindro.matrix_world  @ cilindro.data.vertices[verts_loopcut_right[8]].co
                        # semicirc_radio = (median_point - right_extreme_vertice).length #es 1
                        
                        # right_radio = radio_cilindro + w_right
                        
                        # radio_diff = left_radio - right_radio
                        # resize_value = semicirc_radio - radio_diff
                        # resize_scale = resize_value/semicirc_radio
                        # if frame == 124 or frame == 89 or frame == 90 or frame == 146: print("escala:",resize_scale)
                        
                        # bpy.ops.object.mode_set(mode='EDIT')
                        
                        # bpy.ops.transform.resize(value=(resize_scale, resize_scale, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=prop_size, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)                      

                    elif w_left < w_right:
                        right_radio = radio_cilindro + w_right
                        resize_scale = right_radio / radio_cilindro
                        
                        bpy.ops.object.mode_set(mode='OBJECT')
                        for vert in verts_loopcut:
                            cilindro.data.vertices[vert].select = True #Solo funciona en object mode

                        bpy.ops.object.mode_set(mode='EDIT')
                        #Solo funciona en Edit:
                        bpy.ops.transform.resize(value=(resize_scale, resize_scale, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.8, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.mode_set(mode='EDIT')

                        bpy.ops.mesh.select_all(action='DESELECT') #para deseleccionar todos los edges y verts

                        bpy.ops.object.mode_set(mode='OBJECT')

                        left_extr_vert = cilindro.data.vertices[verts_loopcut[8]]
                        right_extr_vert = cilindro.data.vertices[verts_loopcut[24]]

                        right_co = cilindro.matrix_world @ right_extr_vert.co
                        left_co = cilindro.matrix_world @ left_extr_vert.co

                        prop_size = (left_co - right_co).length

                        move_dist = w_left - w_right

                        left_extr_vert.select = True

                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.transform.translate(value=(move_dist, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=prop_size, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

                    #     median_point = Vector()
                    #     bpy.ops.object.mode_set(mode='OBJECT')
                    #     for vert in verts_loopcut_left:
                    #         cilindro.data.vertices[vert].select = True
                    #         median_point += cilindro.matrix_world @ cilindro.data.vertices[vert].co
                            
                    #     cilindro.data.vertices[verts_loopcut_right[0]].select = True #ahora es una medialuna, mas facil
                    #     median_point += cilindro.matrix_world  @ cilindro.data.vertices[verts_loopcut_right[0]].co
                    #     median_point /= (len(verts_loopcut_left) + 1)
                        
                    #     right_extreme_vertice = cilindro.matrix_world  @ cilindro.data.vertices[verts_loopcut_right[8]].co
                    #     prop_size = (median_point - right_extreme_vertice).length
                        
                    #     left_extreme_vertice = cilindro.matrix_world  @ cilindro.data.vertices[verts_loopcut_left[8]].co
                    #     semicirc_radio = (median_point - left_extreme_vertice).length #es 1
                        
                    #     left_radio = radio_cilindro + w_left
                        
                    #     radio_diff = right_radio - left_radio
                    #     resize_value = semicirc_radio - radio_diff
                    #     resize_scale = resize_value/semicirc_radio
                    #     if frame == 124 or frame == 89 or frame == 90 or frame == 146: print("escala:",resize_scale)
                        
                    #     bpy.ops.object.mode_set(mode='EDIT')
                    #     bpy.ops.transform.resize(value=(resize_scale, resize_scale, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=prop_size, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

                    else: #es probable q sean iguales, asi q sera un scale simple
                        new_radio = radio_cilindro + w_right
                        resize_scale = new_radio / radio_cilindro
                        
                        bpy.ops.object.mode_set(mode='OBJECT')
                        for vert in verts_loopcut:
                            cilindro.data.vertices[vert].select = True
                            
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.transform.resize(value=(resize_scale, resize_scale, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.8, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                    
                    #bpy.ops.object.mode_set(mode='OBJECT')
                    #for vert in verts_loopcut: 
                    #    cilindro.data.vertices[vert].select = True #Solo funciona en object mode
                    # bpy.context.view_layer.objects.active = cilindro
                    # bpy.ops.anim.insert_keyframe_animall()
                    
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT') #para deseleccionar todos los edges y verts
                    
                    bpy.ops.mesh.reveal(select=False) #para revelar
                    
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.context.view_layer.objects.active = cilindro
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.anim.insert_keyframe_animall()

            # Bindear cilindro y armature
            bpy.ops.object.mode_set(mode='OBJECT') 
            bpy.context.scene.frame_set(0)
            bpy.context.view_layer.objects.active = armature
            
            armature.select_set(True)
            cilindro.select_set(True)

            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            bpy.ops.object.select_all(action='DESELECT')

            # Bindear llama y cilindro
            mesh_def = llama.modifiers.new(name="MeshDeform", type='MESH_DEFORM')
            mesh_def.object = cilindro
            mesh_def.use_dynamic_bind = True
            bpy.context.view_layer.objects.active = llama
            bpy.ops.object.meshdeform_bind(modifier='MeshDeform')
            bpy.ops.object.select_all(action='DESELECT')

            temperature = float(lines[-1])
            llama.active_material.node_tree.nodes["Blackbody"].inputs[0].default_value = temperature
            im = bpy.data.images.load(directory + ("//") + "candle-flame_" + flame_name + ".jpg")
            llama.active_material.node_tree.nodes["Image Texture"].image = im
            #bpy.data.images['candle-flame.jpg'].filepath = directory + ("//") + "candle-flame_" + flame_name + ".jpg" #CAMBIABLE?
            cilindro.hide_set(True)
            cilindro.hide_render = True
        else:
            print("El bounding cylinder ya existe")
    else:
        print("Armature no encontrado.") 
