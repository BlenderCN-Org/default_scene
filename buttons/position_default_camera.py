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

class SCENE_OT_position_default_camera(bpy.types.Operator):
    """create (or update/delete) scene with custom default lighting and world settings"""
    bl_idname = "scene.position_default_camera"
    bl_label = "Position Default Camera"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        cam_ob = bpy.data.objects.get("Default_Scene_camera_object")
        return cam_ob is not None and context.scene.ds_include_camera

    def execute(self, context):
        self.start()
        # create timer for modal
        wm = bpy.context.window_manager
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "RET":
            return self.end_commit()
        if event.type == "ESC":
            return self.end_cancel()
        self.actions.update(context, event, print_actions=False)
        return {"PASS_THROUGH"} if self.actions.navigating() or event.type == "RIGHTMOUSE" else {"RUNNING_MODAL"}

    ###################################################
    # initialization method

    def __init__(self):
        self.cam_ob = bpy.data.objects.get("Default_Scene_camera_object")
        self.actions = Actions(bpy.context, {})
        self.last_mx = self.cam_ob.matrix_world

    ###################################################
    # class methods

    def start(self):
        bpy.context.window.cursor_set("SCROLL_XY")
        self.viewCamera()
        setLockCameraToView(True)
        parent_clear(self.cam_ob)

    def end(self):
        bpy.context.window.cursor_set("DEFAULT")
        setLockCameraToView(False)
        # self.viewLast()
        p1 = bpy.data.objects.get("Default_Scene_parent_1")
        if p1 is not None:
            self.cam_ob.parent = p1
            self.cam_ob.matrix_parent_inverse = p1.matrix_world.inverted()

    def end_commit(self):
        self.end()
        return {"FINISHED"}

    def end_cancel(self):
        self.end()
        self.cam_ob.matrix_world = self.last_mx
        return {"CANCELLED"}

    def viewCamera(self):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                self.last_view_perspective = area.spaces[0].region_3d.view_perspective
                area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break

    def viewLast(self):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = self.last_view_perspective

    #############################################
