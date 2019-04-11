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

# System imports
import os
from math import radians

# Blender imports
import bpy
from mathutils import Vector

# Addon imports
from ..functions import *

class SCENE_OT_delete_default_scene(bpy.types.Operator):
    """remove lights and camera created by default scene setup"""
    bl_idname = "scene.delete_default_scene"
    bl_label = "Remove Default Scene Objects"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        return scn.ds_scene_created

    def execute(self, context):
        scn = context.scene
        self.removeObjects()
        scn.ds_scene_created = False

    #############################################
    # class methods

    def removeObjects(self):
        scn = bpy.context.scene
        cam_ob = bpy.data.objects.get("Default_Scene_camera_object")
        emit1 = bpy.data.objects.get("Default_Scene_emitter_1")
        emit2 = bpy.data.objects.get("Default_Scene_emitter_2")
        emit3 = bpy.data.objects.get("Default_Scene_emitter_3")
        parent1 = bpy.data.objects.get("Default_Scene_parent_1")
        parent2 = bpy.data.objects.get("Default_Scene_parent_2")
        parent3 = bpy.data.objects.get("Default_Scene_parent_3")
        allObjs = [cam_ob, emit1, emit2, emit3, parent1, parent2, parent3]
        delete(allObjs)
        tag_redraw_areas(areaTypes=["VIEW_3D"])

    #############################################
