import bpy
from bpy import context

walk_nav = bpy.context.preferences.inputs.walk_navigation
walk_nav.walk_speed = 3

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        with bpy.context.temp_override(area=area, region=area.regions[-1]):
            bpy.ops.view3d.walk('INVOKE_DEFAULT')
        break