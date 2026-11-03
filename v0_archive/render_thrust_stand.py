"""Render the assembled thrust stand in Blender, VTOL-style: 5 angles.

Run headless: blender -b -P render_thrust_stand.py
STL local frames (mm) -> assembly (m): board top z=0, post at x=0,
motor shaft z=0.220, pivot z=0.700, mast foot centre x=-0.230.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

STL_DIR = "/home/hatch/workspace/thrust-stand/stl"
OUT_DIR = "/home/hatch/workspace/thrust-stand/renders"
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------- scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
             bpy.data.lights):
    for item in coll:
        coll.remove(item)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.eevee.taa_render_samples = 64
scene.eevee.use_soft_shadows = True
world = bpy.data.worlds.new("World")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.96, 0.96, 0.96, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
scene.world = world


def mat(name, color, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    return m


M_PETG = mat("PETG", (0.62, 0.72, 0.82), 0.55)
M_TUBE = mat("Tube", (0.95, 0.95, 0.93), 0.35)
M_BOARD = mat("Board", (0.78, 0.62, 0.40), 0.85)
M_MOTOR = mat("Motor", (0.85, 0.55, 0.15), 0.4)
M_PROP = mat("Prop", (0.08, 0.08, 0.08), 0.5)
M_SCALE = mat("Scale", (0.20, 0.20, 0.22), 0.5)
M_LINK = mat("Link", (0.80, 0.15, 0.15), 0.5)
M_BATT = mat("Battery", (0.15, 0.20, 0.45), 0.6)
M_FLOOR = mat("Floor", (0.90, 0.90, 0.90), 1.0)
M_STEEL = mat("Steel", (0.55, 0.55, 0.58), 0.35)


def paint(obj, material):
    obj.data.materials.append(material)


def import_stl(name, loc_m):
    """Import an STL (mm coords), bake a 0.001 scale, place at loc (m).
    The importer leaves earlier objects selected, so the new object must
    be taken from active_object, not selected_objects[0]."""
    path = os.path.join(STL_DIR, name + ".stl")
    bpy.ops.object.select_all(action="DESELECT")
    try:
        bpy.ops.wm.stl_import(filepath=path)
    except Exception:
        bpy.ops.import_mesh.stl(filepath=path)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (0.001, 0.001, 0.001)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth_by_angle(angle=0.5236)
    obj.location = loc_m
    paint(obj, M_PETG)
    return obj


def box(name, size, loc, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = size
    paint(obj, material)
    return obj


def cyl(name, radius, depth, loc, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        location=loc, rotation=rot, vertices=48)
    obj = bpy.context.active_object
    obj.name = name
    paint(obj, material)
    return obj


# ---------------------------------------------------------------- parts
# Printed parts (STL local origin -> assembly position, metres)
import_stl("post_foot", (0, 0, 0))
import_stl("pivot_clevis", (0, 0, 0.635))
import_stl("arm_hub", (0, 0, 0.652))
import_stl("motor_clamp", (0, 0, 0.220))
import_stl("motor_plate_2212", (0.032, 0, 0.220))
# Scale line offset 30 mm sideways (y) so it clears the brace plane.
import_stl("scale_mast", (-0.230, 0.030, 0))
import_stl("scale_platform", (-0.230, 0.030, 0.204))
link = import_stl("scale_link", (-0.107, 0.030, 0.222))
link.data.materials.clear()
paint(link, M_LINK)
import_stl("brace_clamp", (0, 0, 0.350))
import_stl("brace_foot", (-0.350, 0, 0))

# Tubes (his rods)
cyl("post_tube", 0.0127, 0.635, (0, 0, 0.3175), M_TUBE)
cyl("arm_tube", 0.0127, 0.500, (0, 0, 0.432), M_TUBE)
cyl("axle", 0.00733, 0.110, (0, 0, 0.700), M_TUBE, rot=(math.radians(90), 0, 0))
cyl("brace_tube", 0.00733, 0.495, (-0.175, 0, 0.175), M_TUBE,
    rot=(0, math.radians(45), 0))

# Board, battery, ESC, scale, hook
box("board", (0.700, 0.400, 0.018), (-0.150, 0, -0.009), M_BOARD)
box("battery", (0.140, 0.040, 0.035), (-0.120, 0, 0.0175), M_BATT)
box("esc", (0.012, 0.030, 0.050), (0, 0.019, 0.400), M_SCALE)
box("scale_body", (0.130, 0.040, 0.025), (-0.237, 0.030, 0.2215), M_SCALE)
bpy.ops.mesh.primitive_torus_add(major_radius=0.008, minor_radius=0.002,
                                 location=(-0.172, 0.030, 0.2215),
                                 rotation=(math.radians(90), 0, 0))
hook = bpy.context.active_object
hook.name = "scale_hook"
paint(hook, M_STEEL)

# Motor (2212): bell, shaft, prop hub, 2 blades, spinner
cyl("motor_bell", 0.014, 0.026, (0.047, 0, 0.220), M_MOTOR,
    rot=(0, math.radians(90), 0))
cyl("motor_shaft", 0.0025, 0.012, (0.066, 0, 0.220), M_STEEL,
    rot=(0, math.radians(90), 0))
cyl("prop_hub", 0.006, 0.008, (0.072, 0, 0.220), M_PROP,
    rot=(0, math.radians(90), 0))
blade1 = box("prop_blade_1", (0.003, 0.025, 0.120), (0.076, 0, 0.2885),
             M_PROP, rot=(0, 0, math.radians(20)))
bpy.context.view_layer.update()
shaft_c = Vector((0.076, 0, 0.220))
rot_x = Matrix.Rotation(math.pi, 4, "X")
trans = Matrix.Translation(shaft_c)
blade2 = blade1.copy()
blade2.data = blade1.data.copy()
bpy.context.collection.objects.link(blade2)
blade2.name = "prop_blade_2"
blade2.matrix_world = trans @ rot_x @ trans.inverted() @ blade1.matrix_world
cyl("spinner", 0.004, 0.006, (0.079, 0, 0.220), M_STEEL,
    rot=(0, math.radians(90), 0))

# Floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.018))
floor = bpy.context.active_object
floor.name = "floor"
paint(floor, M_FLOOR)

# ---------------------------------------------------------------- lights
def area_light(name, energy, size, loc, target):
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    light.data.size = size
    direction = Vector(target) - Vector(loc)
    light.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return light


area_light("key", 900, 3.0, (2.5, -3.0, 4.0), (0, 0, 0.3))
area_light("fill", 300, 3.0, (-3.0, 2.0, 3.0), (0, 0, 0.3))

# ---------------------------------------------------------------- cameras
def camera(name, loc, target):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.name = name
    cam.data.lens = 50
    cam.data.sensor_fit = "VERTICAL"
    direction = Vector(target) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return cam


VIEWS = [
    ("01_isometric", (0.95, -1.15, 0.85), (-0.15, 0, 0.35)),
    ("02_side", (0, -1.80, 0.35), (-0.15, 0, 0.35)),
    ("03_front_prop", (1.80, 0, 0.35), (-0.15, 0, 0.35)),
    ("04_top", (0, 0, 1.60), (-0.15, 0, 0)),
    ("05_motor_closeup", (0.45, -0.45, 0.45), (-0.08, 0, 0.22)),
]
# Sanity check: the whole stand must span roughly x -0.5..0.2, z -0.02..0.73.
bpy.context.view_layer.update()
mins = [1e9] * 3
maxs = [-1e9] * 3
for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    for corner in obj.bound_box:
        world = obj.matrix_world @ Vector(corner)
        for i in range(3):
            mins[i] = min(mins[i], world[i])
            maxs[i] = max(maxs[i], world[i])
print("scene bbox min", [round(v, 3) for v in mins],
      "max", [round(v, 3) for v in maxs])
if os.environ.get("TEST"):
    scene.render.resolution_percentage = 50
    VIEWS = VIEWS[:2]
if os.environ.get("ONLY"):
    VIEWS = [v for v in VIEWS if os.environ["ONLY"] in v[0]]
for name, loc, target in VIEWS:
    cam = camera("cam_" + name, loc, target)
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT_DIR, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("rendered", name)
print("done")
