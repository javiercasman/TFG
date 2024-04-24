bl_info = {
    "name": "Spawn Flame",
    "blender": (4, 0, 0),
    "category": "Object",
}

import bpy
import math
import mathutils
from bpy.types import Operator, AddonPreferences
from bpy.props import FloatVectorProperty

# Operator para spawnear un cubo y controlar su posición
class SpawnCubeOperator(Operator):
    bl_idname = "object.spawn_cube"
    bl_label = "Spawn Cube"
    bl_description = "Spawn a cube in front of the camera and enter edit mode to modify its position"

    def execute(self, context):
        # Obtener la ubicación y rotación de la cámara
        camera = bpy.context.scene.camera
        camera_location = camera.location
        camera_rotation = camera.rotation_euler.to_matrix().to_3x3()

        # Calcular la posición del cubo enfrente de la cámara
        cube_distance = 1.0  # Distancia desde la cámara
        cube_scale = 0.1  # Escala del cubo
        cube_position = camera_location + rcube_distance * camera_rotation @ mathutils.Vector((0, 0, 1))

        # Crear un cubo
        bpy.ops.mesh.primitive_cube_add(location=cube_position, scale=(cube_scale, cube_scale, cube_scale))

        # Guardar la ubicación del cubo para modificarla después
        context.scene.spawned_cube_location = cube_position

        # Cambiar al modo de edición para modificar la posición del cubo
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

# Operator para confirmar la posición del cubo y salir del modo de edición
class ConfirmCubePositionOperator(Operator):
    bl_idname = "object.confirm_cube_position"
    bl_label = "Confirm Cube Position"
    bl_description = "Confirm the position of the cube and return to walk navigation mode"

    def execute(self, context):
        # Salir del modo de edición
        bpy.ops.object.mode_set(mode='OBJECT')

        # Volver al modo walk navigation
        activate_walk_navigation()

        return {'FINISHED'}

# AddonPreferences para guardar el estado del modo walk navigation
class WalkNavigationPreferences(AddonPreferences):
    bl_idname = __name__

    walk_navigation_location: FloatVectorProperty(
        name="Walk Navigation Location",
        description="Location where walk navigation will be activated",
        default=(0.0, 0.0, 0.0),  # Cambiado a un valor único en lugar de una tupla
        subtype='XYZ'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "walk_navigation_location")

class ConfigureWalkNavigationOperator(Operator):
    bl_idname = "object.configure_walk_navigation"
    bl_label = "Configure Walk Navigation"
    bl_description = "Configure Walk Navigation mode and controls"

    def execute(self, context):
        # 1. Activar el modo de navegación estilo "Walk Navigation"
        walk_nav = bpy.context.preferences.inputs.walk_navigation
        walk_nav.walk_speed = 3

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                with bpy.context.temp_override(area=area, region=area.regions[-1]):
                    bpy.ops.view3d.walk('INVOKE_DEFAULT')
                break

        # 2. Modificar los controles para que no se pueda salir del modo "Walk Navigation"
        walk_nav_preferences = context.preferences.inputs.walk_navigation
        walk_nav_preferences.enable_pie_menu = False
        walk_nav_preferences.enable_pan = False
        walk_nav_preferences.enable_rotate = False
        walk_nav_preferences.enable_zoom = False
        walk_nav_preferences.enable_walk = True

        # 3. Asignar la tecla "T" para spawnear un cubo mientras estás en modo "Walk Navigation"
        keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='Walk Navigation', space_type='VIEW_3D')
        keymap_item = keymap.keymap_items.new('object.spawn_cube', 'T', 'PRESS', ctrl=False, shift=False, alt=False)

        return {'FINISHED'}

# Registrar clases
classes = (
    SpawnCubeOperator,
    ConfirmCubePositionOperator,
    WalkNavigationPreferences,
    ConfigureWalkNavigationOperator
)

def activate_walk_navigation():
    walk_nav = bpy.context.preferences.inputs.walk_navigation
    walk_nav.walk_speed = 3

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            with bpy.context.temp_override(area=area, region=area.regions[-1]):
                bpy.ops.view3d.walk('INVOKE_DEFAULT')
            break

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.spawned_cube_location = bpy.props.FloatVectorProperty(
        name="Spawned Cube Location",
        subtype='XYZ',
    )
    #activate_walk_navigation()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.spawned_cube_location

if __name__ == "__main__":
    register()