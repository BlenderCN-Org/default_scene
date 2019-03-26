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
    "blender"     : (2, 79, 0),
    "description" : "Create quick default scene for quick and easy scene setup/rendering",
    "location"    : "VIEW_3D > Tools > Bricker > Default Scene",
    "warning"     : "Work in progress",
    "wiki_url"    : "",
    "tracker_url" : "",
    "category"    : "World"}

# System imports
# NONE!

# Blender imports
import bpy
from bpy.props import *
props = bpy.props

# Addon imports
from .ui import *
from .buttons import *

def updateScale(self, context):
    scn = context.scene
    parent = bpy.data.objects.get('Default_Scene_parent_1')
    if parent:
        parent.scale = (scn.ds_scale, scn.ds_scale, scn.ds_scale)

def register():
    bpy.utils.register_class(VIEW3D_PT_default_scene)
    bpy.utils.register_class(SCENE_OT_create_default_scene)

    bpy.types.Scene.ds_scale = FloatProperty(
        name="Scene Scale",
        description="Scale of scene to create",
        min=0.0001,max=1000,
        update=updateScale,
        default=1.0)
    bpy.types.Scene.ds_include_camera = BoolProperty(
        name="Include Camera",
        description="Add camera to scene in addition to adding lights and world data",
        default=True)
    bpy.types.Scene.ds_scene_created = BoolProperty(default=False)

def unregister():
    Scn = bpy.types.Scene

    del Scn.ds_scale
    del Scn.ds_include_camera
    del Scn.ds_scene_created

    bpy.utils.unregister_class(SCENE_OT_create_default_scene)
    bpy.utils.unregister_class(VIEW3D_PT_default_scene)


if __name__ == "__main__":
    register()
