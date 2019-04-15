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

# System imports
import os

# Blender imports
import bpy

# Addon imports
from .common import *


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


def loadHDRI(self, context):
    # get environment texture node
    scn = context.scene
    nt = scn.world.node_tree
    envTexNode = nt.nodes.get("Default World Texture")
    if envTexNode is None:
        return

    # open image
    # addonPath = os.path.join(get_addon_directory(), "textures")
    # bpy.ops.image.open(filepath="//textures/studio_small_01_4k.hdr", directory=addonPath, files=[{"name":"studio_small_01_4k.hdr"}], show_multiview=False)
    # envTexNode.image = bpy.data.images["studio_small_01_4k.hdr"]
    name = "studio_small_01_{res}.hdr".format(res=scn.hdri_resolution)
    im_path = os.path.join(get_addon_directory(), "textures", name)
    im = bpy.data.images.get(name)
    if im is None:
        bpy.ops.image.open(filepath=im_path)
        im = bpy.data.images[name]
    envTexNode.image = im
