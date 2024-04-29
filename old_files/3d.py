import bpy
from mathutils import Vector

def find_area():
    try:
        for a in bpy.data.window_managers[0].windows[0].screen.areas:
            if a.type == "VIEW_3D":
                return a
        return None
    except:
        return None

area = find_area()

if area is None:
    print("area not find")
else:
    # print(dir(area))
    r3d = area.spaces[0].region_3d
    view_mat = r3d.perspective_matrix
    print("view matrix: ", view_mat)
    
    loc, rot, sca = view_mat.decompose()
    #cam_direction = view_mat.to_quaternion() @ Vector((0.0, 0.0, -1.0))
    cam_direction = view_mat.to_3x3().row[2]

    print("location xyz: ", loc)
    print("rotation wxyz: ", rot)
    print("scale xyz: ", sca)
    print("")
    print("view_distance: ", r3d.view_distance)
    print("view_location: ", r3d.view_location)
    print("view_rotation: ", r3d.view_rotation)
    print("view_camera_zoom: ", r3d.view_camera_zoom)
    print("view_distance: ", r3d.view_distance)
    print("view_camera_offset: ", r3d.view_camera_offset)
    print(cam_direction)