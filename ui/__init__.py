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

# Blender imports
import bpy
from bpy.props import *
from bpy.types import Panel

# Addon imports
from ..functions.common import *


class SCENE_PT_default_scene(Panel):
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "scene"
    bl_label       = "Default Scene"
    bl_idname      = "SCENE_PT_default_scene"
    COMPAT_ENGINES = {"CYCLES", "BLENDER_EEVEE"}

    # @classmethod
    # def poll(cls, context):
    #     """ Only renders UI if cycles render engine is used """
    #     return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        col = layout.column(align=True)
        row = col.row(align=True)

        if context.engine not in self.COMPAT_ENGINES:
            row.label(text="Please switch to the 'CYCLES' or 'EEVEE' render engine")
            return

        if not scn.ds_scene_created:
            row.operator("scene.setup_default_scene", icon="IMPORT")
        else:
            row.operator("scene.position_default_camera", icon="CAMERA_DATA")
            row = col.row(align=True)
            row.operator("scene.delete_default_scene", icon="CANCEL")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scn, "ds_include_camera")

        parent1 = bpy.data.objects.get('Default_Scene_parent_1')
        parent2 = bpy.data.objects.get('Default_Scene_parent_2')

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Scene Scale")
        row = col.row(align=True)
        row.column().prop(scn, "ds_scale", text="XYZ")
        # if parent1 is not None:
        #     row = col.row(align=True)
        #     row.column().prop(parent1, "location", text="Scene Location")
        if parent2 is not None:
            row = col.row(align=True)
            if parent2.rotation_mode == 'QUATERNION':
                row.column().prop(parent2, "rotation_quaternion", text="Lighting Rotation")
            elif parent2.rotation_mode == 'AXIS_ANGLE':
                row.column().prop(parent2, "rotation_axis_angle", text="Lighting Rotation")
            else:
                row.column().prop(parent2, "rotation_euler", text="Lighting Rotation")
