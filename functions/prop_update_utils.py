# Copyright (C) 2018 Christopher Gearhart
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

# Blender imports
import bpy


def updateScale(self, context):
    scn = context.scene
    parent = bpy.data.objects.get('Default_Scene_parent_1')
    if parent:
        parent.scale = (scn.ds_scale, scn.ds_scale, scn.ds_scale)


def updateCamera(self, context):
    scn = context.scene
    if scn.ds_include_camera:
        enableDefaultCamera()
    else:
        cam_ob = bpy.data.objects.get("Default_Scene_camera_object")
        if cam_ob is not None: unlink_object(cam_ob)
