"""
.OBJ AO bake script

Objectives
----------
-Source is Wavefront OBJ, that is imported
-Meshes from OBJ have UV maps automatically created (skip if UV map already present)
-One texture for each mesh is created and assigned
-Ambient occlusion is mapped to textures
-Textures are saved with filenames reflecting mesh name from OBJ
-OBJs are exported to include new UV coordinates
"""

import bpy
import os

# Use enviroment variable to get path to source obj
# so we can create useful batch scripts later
# and prefix for new OBJ with UVs and the baked textures with AO
source_obj = os.getenv("source_obj", "")
dest_prefix = os.getenv("dest_prefix", "")
tex_prefix = os.getenv("tex_prefix", "")
bake_margin = int(os.getenv("bake_margin", "0"))
uv_margin = float(os.getenv("uv_margin", "0"))
obj_dir = os.getenv("obj_dir", "")
tex_dir = os.getenv("tex_dir", "")
tex_res = int(os.getenv("tex_res", "1024"))
number_of_samples = int(os.getenv("number_of_samples", "5"))

# Delete default garbage
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete('EXEC_DEFAULT')

# Import OBJ
bpy.ops.import_scene.obj(filepath = source_obj)

# Should I use bpy.context.scene instead of bpy.data.scenes[0]?
scene = bpy.data.scenes[0]

# Set baking options
scene.render.bake_type = "AO"
scene.render.bake_margin = bake_margin
scene.render.use_bake_normalize = True
# Change samples to avoid grainy AO map (may use grainy AO map for stylistic reasons)
# I thought it was render.bake_samples, but it was a totally different setting instead
# scene.render.bake_samples = number_of_samples
bpy.data.worlds["World"].light_settings.samples = number_of_samples

for obj in bpy.data.objects:
	# Unselect all
	obj.select = False
	# Also, remove "_default" suffix added by OBJ importer
	if len(obj.name) - len("_default") == obj.name.rfind("_default"):
		obj.name = obj.name[:obj.name.rfind("_default")]

# Remove "_default" suffix added by OBJ importer in mesh names too
for mesh in bpy.data.meshes:
	if len(mesh.name) - len("_default") == mesh.name.rfind("_default"):
		mesh.name = mesh.name[:mesh.name.rfind("_default")]

for obj in bpy.data.scenes[0].objects:
	if obj.type != 'MESH':
		continue
	
	# Select object and make active
	scene.objects.active = obj
	obj.select = True
	
	# Automatically create the UV map using smart projection
	# Skipped if object already has one UV layer
	if len(bpy.context.object.data.uv_layers.keys()) <= 0:
		# Note: setting angle limit to 0 avoids overlapping faces in the generated UV map
		bpy.ops.uv.smart_project(angle_limit=0.0, island_margin=uv_margin, user_area_weight=1.0)
	
	# Now a texture should be created and assigned to the object, to which the AO will be baked
	new_image = bpy.data.images.new(name = tex_prefix + obj.name, width=tex_res, height=tex_res)
	for uv_face in obj.data.uv_textures.active.data:
		uv_face.image = new_image
	
	# Now do the baking
	bpy.ops.object.bake_image()
	
	# Unselect the object
	obj.select = False

# Save the textures
# This part must be modified to use names of objects the texture is assigned to
for image in bpy.data.images:
	if image.is_dirty:
		image.filepath_raw = os.getcwd() + "/" + tex_dir + image.name + ".png"
		image.save()

# Re-export objs
bpy.ops.export_scene.obj(filepath = os.getcwd() + "/" + obj_dir + dest_prefix + source_obj, axis_forward = '-Z', axis_up = 'Y')