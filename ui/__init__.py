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
    COMPAT_ENGINES = {"CYCLES"}

    @classmethod
    def poll(cls, context):
        """ Only renders UI if cycles render engine is used """
        return (context.engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        col = layout.column(align=True)
        row = col.row(align=True)
        if not scn.ds_scene_created:
            row.operator("scene.create_default_scene", text="Create Default Scene", icon="IMPORT").action = "CREATE"
        else:
            row.operator("scene.create_default_scene", text="Update Default Scene", icon="FILE_REFRESH").action = "UPDATE"
            row = col.row(align=True)
            row.operator("scene.create_default_scene", text="Delete Default Scene", icon="CANCEL").action = "DELETE"

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
