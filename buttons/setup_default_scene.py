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

class SCENE_OT_setup_default_scene(bpy.types.Operator):
    """setup active scene with custom default lighting and world settings"""
    bl_idname = "scene.setup_default_scene"
    bl_label = "Setup Default Scene"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        # return bpy.context.active_object is not None
        return True

    def execute(self, context):
        scn = context.scene

        parent1, parent2 = self.addParentObj()

        self.setWorldValues()
        l1, l2, l3 = self.addLightObjects(parent2)
        self.cam_ob = self.addCameraObject(parent1, include=scn.ds_include_camera)

        cm = None if not isBrickerInstalled() or scn.cmlist_index == -1 else scn.cmlist[scn.cmlist_index]
        parent1.location = self.orig_active_obj.location if cm is None else bounds(cm.source_obj).mid

        if scn.ds_include_camera:
            self.cam_ob.data.dof_object = self.orig_active_obj if cm is None else cm.source_obj
            self.cam_ob.data.cycles.aperture_type = 'FSTOP'
            self.cam_ob.data.cycles.aperture_fstop = 1

        scn.ds_scene_created = True
        setActiveObj(self.orig_active_obj)
        select(self.orig_selection, only=True)

        return {"FINISHED"}

    ###################################################
    # initialization method

    def __init__(self):
        self.orig_active_obj = bpy.context.active_object
        self.orig_selection = bpy.context.selected_objects

    #############################################
    # class methods

    def setWorldValues(self):
        scn = bpy.context.scene
        scn.world.use_nodes = True
        scn.world.light_settings.use_ambient_occlusion = False

        #select world node tree
        nt = scn.world.node_tree

        #create new environment texture node if it doesn't already exist
        envTexNode = nt.nodes.get("Default World Texture")
        if not envTexNode:
            envTexNode = nt.nodes.new(type="ShaderNodeTexEnvironment")
            envTexNode.name = "Default World Texture"

        # get world output node
        worldOutNode = nt.nodes.get("World Output")
        # ensure background node exists and is connected to world output node
        backNode = nt.nodes.get('Background')
        backConnected = False
        if backNode is not None:
            for link in backNode.outputs['Background'].links:
                if link.to_node == worldOutNode:
                    backConnected = True
        if backNode is None:
            backNode = nt.nodes.new('ShaderNodeBackground')
            backNode.location = worldOutNode.location
        if not backConnected:
            backBackOut = backNode.outputs['Background']
            worldSurfIn = worldOutNode.inputs['Surface']
            nt.links.new(backBackOut, worldSurfIn)
        # position envTexNode to left of background node
        envTexNode.location = backNode.location - Vector((300, 0))

        # connect color out of envTexNode to Color in of background node
        envTexColOut = envTexNode.outputs['Color']
        backColIn = backNode.inputs['Color']
        nt.links.new(envTexColOut, backColIn)

        # add texture mapping nodes
        texNode = nt.nodes.get('Texture Coordinate')
        if texNode is None:
            texNode = nt.nodes.new('ShaderNodeTexCoord')
        texNode.location = envTexNode.location - Vector((650, 0))
        mapNode = nt.nodes.get('Mapping')
        if mapNode is None:
            mapNode = nt.nodes.new('ShaderNodeMapping')
        mapNode.location = texNode.location + Vector((250, 0))
        nt.links.new(texNode.outputs[0], mapNode.inputs[0])
        nt.links.new(mapNode.outputs[0], envTexNode.inputs[0])


        # set backNode strength value
        backNode.inputs["Strength"].default_value = 0.9
        # set backNode image value
        loadHDRI(self, bpy.context)

    def addParentObj(self):
        scn = bpy.context.scene

        parent1 = bpy.data.objects.new("Default_Scene_parent_1", None)
        parent1.scale = (scn.ds_scale, scn.ds_scale, scn.ds_scale)
        parent2 = bpy.data.objects.new("Default_Scene_parent_2", None)
        parent2.parent = parent1

        return parent1, parent2

    def addCameraObject(self, parent=None, include=True):
        scn = bpy.context.scene

        cam = bpy.data.cameras.new("Default_Scene_camera")
        cam_ob = bpy.data.objects.new("Default_Scene_camera_object", cam)
        cam_ob.location = (1.2, -4, 1.4)
        cam_ob.rotation_euler = (1.2708, 0, 0.3)

        if parent:
            cam_ob.parent = parent

        if include:
            link_object(cam_ob)
            select(cam_ob, active=cam_ob)
            scn.camera = cam_ob

        return cam_ob

    def addLightObjects(self, parent=None):
        scn = bpy.context.scene
        last_render_engine = scn.render.engine
        scn.render.engine = "CYCLES"

        # emit1_color = (0.576, 0.824, 0.953, 1)
        # emit2_color = (0.529, 0.733, 0.922, 1)
        # emit3_color = (1, 1, 0.95, 1)
        emit1_color = (1, 1, 1, 1)
        emit2_color = (1, 1, 1, 1)
        emit3_color = (1, 1, 1, 1)
        emit1_energy = 1
        emit2_energy = 1
        emit3_energy = 1

        # add area lamp 1
        light_add(type='AREA')
        emit1 = bpy.context.active_object
        emit1.name = "Default_Scene_emitter_1"
        if b280(): emit1.data.size = 0.1
        # CYCLES
        nodes = emit1.data.node_tree.nodes
        nodes["Emission"].inputs[0].default_value = emit1_color
        nodes["Emission"].inputs[1].default_value = emit1_energy * 100
        # lf = nodes.new('ShaderNodeLightFalloff')
        # lf.inputs[0].default_value = emit1_energy * 100  # 175
        # links = emit1.data.node_tree.links
        # links.new(lf.outputs[0], nodes["Emission"].inputs[1])
        # EEVEE
        emit1.data.color = emit1_color[:3]
        emit1.data.energy = emit1_energy


        # add area lamp 2
        light_add(type='AREA')
        emit2 = bpy.context.active_object
        emit2.name = "Default_Scene_emitter_2"
        if b280(): emit2.data.size = 0.1
        # CYCLES
        nodes = emit2.data.node_tree.nodes
        nodes["Emission"].inputs[0].default_value = emit2_color
        nodes["Emission"].inputs[1].default_value = emit2_energy * 100
        # lf = nodes.new('ShaderNodeLightFalloff')
        # lf.inputs[0].default_value = emit2_energy * 100  # 160
        # links = emit2.data.node_tree.links
        # links.new(lf.outputs[0], nodes["Emission"].inputs[1])
        # EEVEE
        emit2.data.color = emit2_color[:3]
        emit2.data.energy = emit2_energy

        # add area lamp 3
        light_add(type='AREA')
        emit3 = bpy.context.active_object
        emit3.name = "Default_Scene_emitter_3"
        if b280(): emit3.data.size = 0.1
        # CYCLES
        nodes = emit3.data.node_tree.nodes
        nodes["Emission"].inputs[0].default_value = emit3_color
        nodes["Emission"].inputs[1].default_value = emit3_energy * 100
        # lf = nodes.new('ShaderNodeLightFalloff')
        # lf.inputs[0].default_value = emit3_energy * 100  # 100
        # links = emit3.data.node_tree.links
        # links.new(lf.outputs[0], nodes["Emission"].inputs[1])
        # EEVEE
        emit3.data.color = emit3_color[:3]
        emit3.data.energy = emit3_energy

        emit1.location = (2.5, 0, 1.2)
        emit1.rotation_euler = (radians(70), radians(-12), radians(90))
        emit1.scale = (30, 25, 30)

        emit2.location = (-1.8, -0.8, 0.6)
        emit2.rotation_euler = (radians(90), radians(-3), radians(-70))
        emit2.scale = (25, 20, 30)

        emit3.location = (0.25, 0.53, 1.75)
        emit3.rotation_euler = (radians(-4), radians(4), radians(35))
        emit3.scale = (30, 10, 20)

        if parent:
            emit1.parent = parent
            emit2.parent = parent
            emit3.parent = parent

        scn.render.engine = last_render_engine

        return emit1, emit2, emit3

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
