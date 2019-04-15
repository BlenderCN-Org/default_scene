# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name"        : "Default Scene",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (0, 1, 0),
    "blender"     : (2, 80, 0),
    "description" : "Create quick default scene for quick and easy scene setup/rendering",
    "location"    : "Properties > Scene > Default Scene",
    "warning"     : "Work in progress",
    "wiki_url"    : "",
    "tracker_url" : "",
    "category"    : "World"}

# System imports
# NONE!

# Blender imports
import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class
props = bpy.props

# Addon imports
from .ui import *
from .buttons import *
from .functions.common import *
from .functions.prop_update_utils import *

classes = (
    SCENE_PT_default_scene,
    SCENE_OT_setup_default_scene,
    SCENE_OT_delete_default_scene,
    SCENE_OT_position_default_camera,
)



def register():
    for cls in classes:
        make_annotations(cls)
        register_class(cls)

    bpy.types.Scene.ds_scale = FloatProperty(
        name="Scene Scale",
        description="Scale of scene to create",
        min=0.0001,max=1000,
        update=updateScale,
        default=1.0)
    bpy.types.Scene.ds_include_camera = BoolProperty(
        name="Include Camera",
        description="Add camera to scene in addition to adding lights and world data",
        update=updateCamera,
        default=True)
    bpy.types.Scene.hdri_resolution = EnumProperty(
        name="HDRI Resolution",
        description="Resolution of the HDRI Environment map (1k-16k)",
        items=(("1k", "1k", "Use HDRI map at this resolution"),
               ("2k", "2k", "Use HDRI map at this resolution"),
               ("4k", "4k", "Use HDRI map at this resolution"),
               ("8k", "8k", "Use HDRI map at this resolution"),
               ("16k","16k","Use HDRI map at this resolution")),
        update=loadHDRI,
        default="8k")
    bpy.types.Scene.ds_scene_created = BoolProperty(default=False)

def unregister():
    Scn = bpy.types.Scene

    del Scn.ds_scale
    del Scn.ds_include_camera
    del Scn.ds_scene_created

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
