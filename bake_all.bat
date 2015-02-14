@echo off
setlocal enabledelayedexpansion

if not exist output mkdir output

del /Q output\*.*
del bake_all.log

set source_obj=cabinet.obj
set PATH=C:\Program Files\Blender Foundation\Blender;%PATH%
set number_of_samples=20
set obj_dir=output/
set tex_dir=output/

set objs_baked=0
set objs_total=0

for %%f in (*.obj) do set /a objs_total=!objs_total!+1

cls
echo Baking %objs_total% files...

for %%f in (*.obj) do (
	set source_obj=%%f
	echo. | blender --debug -b -P ao_bake_obj.py >> bake_all.log 2>&1
	set /a objs_baked=!objs_baked!+1
	echo File !objs_baked! of %objs_total% baked.
)

echo %objs_baked% file(s) processed.
pause