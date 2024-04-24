bl_info = {
    "name": "Flame Spawn",
    "blender": (4, 0, 0),
    "category": "Object",
}

import bpy
import math
import mathutils
from bpy.types import Operator, AddonPreferences
from bpy.props import FloatProperty, BoolProperty




#CAMBIAMOS ADD-ON!!!!!!
#Vamos a añadir un simple botón para añadir la llama. No hace falta lo del walk navigation, lo podemos usar pero q no sea obligatorio. Luego añadimos un botón para añdir las llamas, parece bastante mejor y así podemos usar cosas normales de Blender para hacer animaciones.

'''
class MoveFlameModalOperator(Operator): #JUNTAR LAS DOS CLASES.
    bl_idname = "object.move_flame_modal_operator"
    bl_label = "Move flame modal operator"

    scale_factor = FloatProperty(default=0.1)
    cube_spawned = BoolProperty(default=False)

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            # Si se hace clic derecho o se presiona ESC, finalizar el modal operator
            #can_spawn = False ???? no se
            return {'CANCELLED'}
        
        if event.type == 'LEFTMOUSE' and self.cube_spawned:
            # Si se hace clic izquierdo, fijar la posición del cubo
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            return {'FINISHED'}
        
        if event.type == 'T' and not self.cube_spawned:
            # Si se presiona la tecla T, crear un cubo en la posición actual del cursor
            bpy.ops.mesh.primitive_cube_add(location=context.scene.camera.location + mathutils.Vector((0, 0, -2)), scale=(self.scale_factor, self.scale_factor, self.scale_factor))
            self.cube_spawned = True
            return {'RUNNING_MODAL'}

        if event.type == 'O':
            # Si se presiona la tecla O, mover el cubo hacia adelante
            bpy.context.active_object.location.x += 0.1
            return {'RUNNING_MODAL'}

        if event.type == 'L':
            # Si se presiona la tecla L, mover el cubo hacia atrás
            bpy.context.active_object.location.x -= 0.1
            return {'RUNNING_MODAL'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}
'''
class CandlelightExplorer(Operator):
    bl_idname = "object.candlelight_explorer"
    bl_label = "Candlelight Explorer"

    walk_navigation_active = bpy.props.BoolProperty(default=False)
    moving_flame = bpy.props.BoolProperty(default=False)
    scale_factor = FloatProperty(default=0.1) #borrar?

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE' and self.moving_flame:
            loc, dir = camera_param()
            dist = math.dist(context.active_object.location, loc)
            new_loc = dist * dir
            print(new_loc)
            context.active_object.location = new_loc #ns pq, se acumula, no va bien

        if event.type == 'T' and not self.moving_flame:
            self.moving_flame = True
            loc, dir = camera_param()
            bpy.ops.mesh.primitive_cube_add(location=loc + (1.0 * dir), scale=(0.1, 0.1, 0.1))
            #flame = context.active_object
            return {'RUNNING_MODAL'}

        if event.type == 'ESC':
            if not self.moving_flame:
                if self.walk_navigation_active:
                    self.walk_navigation_active = False
            else:
                #bpy.data.objects.remove(flame, do_unlink=True)
                bpy.data.objects.remove(context.active_object, do_unlink=True)
                self.moving_flame = False
            return {'RUNNING_MODAL'}

        if event.type == 'O' and self.moving_flame:
            # Si se presiona la tecla O, mover el cubo hacia adelante
            #flame.location.x += 0.1
            loc, dir = camera_param()
            context.active_object.location += dir @ mathutils.Vector((1.0, 1.0, 1.0))
            return {'RUNNING_MODAL'}

        if event.type == 'L' and self.moving_flame:
            # Si se presiona la tecla L, mover el cubo hacia atrás
            #flame.location.x -= 0.1
            loc, dir = camera_param()
            context.active_object.location -= dir @ mathutils.Vector((1.0, 1.0, 1.0))
            return {'RUNNING_MODAL'}
        
        if event.type == 'LEFTMOUSE':
            if not self.walk_navigation_active:
                activate_walk_navigation(context)
                self.walk_navigation_active = True
                return {'PASS_THROUGH'}
            elif self.moving_flame:
                self.moving_flame = False
                context.active_object
            return {'RUNNING_MODAL'}
            
        return {'PASS_THROUGH'}

    def invoke(self, context, event):  
        activate_walk_navigation(context)
        self.walk_navigation_active = True
        self.moving_flame = False

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

# Registrar clases
classes = (
    CandlelightExplorer
)

def find_area():
    try:
        for a in bpy.data.window_managers[0].windows[0].screen.areas:
            if a.type == "VIEW_3D":
                return a
        return None
    except:
        return None
    
def camera_param():
    area = find_area()
    if area is None:
        print("area not find")
    else:
        # print(dir(area))
        r3d = area.spaces[0].region_3d
        location = r3d.view_location
        view_mat = r3d.perspective_matrix
        direction = view_mat.to_3x3().row[2]
        return location, direction

def activate_walk_navigation(context):
    walk_nav = context.preferences.inputs.walk_navigation
    walk_nav.walk_speed = 3

    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            with context.temp_override(area=area, region=area.regions[-1]):
                bpy.ops.view3d.walk('INVOKE_DEFAULT')
            break

def register():
    # for cls in classes:
    #     bpy.utils.register_class(cls)
    bpy.utils.register_class(CandlelightExplorer)

def unregister():
    #for cls in classes:
    #    bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(CandlelightExplorer)

if __name__ == "__main__":
    register()