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

class SCENE_OT_create_default_scene(bpy.types.Operator):
    """create (or update/delete) scene with custom default lighting and world settings"""
    bl_idname = "scene.create_default_scene"
    bl_label = "Create Default Scene"
    bl_options = {"REGISTER", "UNDO"}


    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        return bpy.context.active_object is not None

    def execute(self, context):
        scn = context.scene
        if scn.ds_scene_created:
            self.removeObjects()
            scn.ds_scene_created = False
            if self.action == "DELETE":
                return{"FINISHED"}

        scn.render.engine = 'CYCLES'

        parent1, parent2 = self.addParentObj()
        self.setWorldValues()
        l1, l2, l3 = self.addLightObjects(parent2)
        self.cam_ob = self.addCameraObject(parent1) if scn.ds_include_camera else None

        cm = None if not isBrickerInstalled() or scn.cmlist_index == -1 else scn.cmlist[scn.cmlist_index]
        if cm is None:
            parent1.location = self.orig_active_obj.location
            self.cam_ob.data.dof_object = self.orig_active_obj
        else:
            source_details = bounds(cm.source_obj)
            parent1.location = source_details.mid
            self.cam_ob.data.dof_object = cm.source_obj
        self.cam_ob.data.cycles.aperture_type = 'FSTOP'
        self.cam_ob.data.cycles.aperture_fstop = 1


        if scn.ds_include_camera:
            self.viewCamera()
        scn.ds_scene_created = True
        setLockCameraToView(True)
        setActiveObj(self.orig_active_obj)
        select(self.orig_selection, only=True)

        # create timer for modal
        wm = bpy.context.window_manager
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        bpy.context.window.cursor_set("SCROLL_XY")
        if event.type in ("ESC", "RET"):
            bpy.context.window.cursor_set("DEFAULT")
            setLockCameraToView(False)
            return {"FINISHED"}
        self.actions.update(context, event, print_actions=False)
        return {"PASS_THROUGH"} if self.actions.navigating() else {"RUNNING_MODAL"}

    def cancel(self, context):
        pass

    ###################################################
    # initialization method

    def __init__(self):
        self.orig_active_obj = bpy.context.active_object
        self.orig_selection = bpy.context.selected_objects
        self.actions = Actions(bpy.context, {})

    ###################################################
    # class variables

    # properties
    action = bpy.props.EnumProperty(
        items=(
            ("CREATE", "Create", ""),
            ("UPDATE", "Update", ""),
            ("DELETE", "Delete", ""),
        ),
        default="CREATE"
    )

    #############################################
    # class methods

    def setWorldValues(self):
        scn = bpy.context.scene
        scn.world.use_nodes = True
        scn.world.light_settings.use_ambient_occlusion = False

        #select world node tree
        wd = scn.world
        nt = bpy.data.worlds[wd.name].node_tree

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
            backNode.location.x = worldOutNode.location.x - 300
            backNode.location.y = worldOutNode.location.y
        if not backConnected:
            backBackOut = backNode.outputs['Background']
            worldSurfIn = worldOutNode.inputs['Surface']
            nt.links.new(backBackOut, worldSurfIn)
        # position envTexNode to left of background node
        envTexNode.location.x = backNode.location.x - 300
        envTexNode.location.y = backNode.location.y

        #Connect color out of envTexNode to Color in of background node
        envTexColOut = envTexNode.outputs['Color']
        backColIn = backNode.inputs['Color']
        nt.links.new(envTexColOut, backColIn)

        #set backNode strength value
        backNode.inputs["Strength"].default_value = 0.9
        #set backNode image value
        addonPath = os.path.dirname(os.path.abspath(__file__))[:-8] + "/textures"
        bpy.ops.image.open(filepath="//textures/studio015.hdr", directory=addonPath, files=[{"name":"studio015.hdr", "name":"studio015.hdr"}], show_multiview=False)
        envTexNode.image = bpy.data.images["studio015.hdr"]

    def addParentObj(self):
        scn = bpy.context.scene

        pm = bpy.data.meshes.new("Default_Scene_parent_m")
        parent1 = bpy.data.objects.new("Default_Scene_parent_1", pm)
        parent1.scale = (scn.ds_scale, scn.ds_scale, scn.ds_scale)
        parent2 = bpy.data.objects.new("Default_Scene_parent_2", pm)
        parent2.parent = parent1

        return parent1, parent2

    def addCameraObject(self, parent=None):
        scn = bpy.context.scene

        cam = bpy.data.cameras.new("Default_Scene_camera")
        cam_ob = bpy.data.objects.new("Default_Scene_camera_object", cam)
        link_object(cam_ob)
        cam_ob.location = (1.2, -4, 1.4)
        cam_ob.rotation_euler = (1.2708, 0, 0.3)

        if parent:
            cam_ob.parent = parent

        select(cam_ob, active=cam_ob)
        scn.camera = cam_ob

        return cam_ob

    def addLightObjects(self, parent=None):
        scn = bpy.context.scene

        # add area lamp 1
        light_add(type='AREA')
        emit1 = bpy.context.active_object
        emit1.name = "Default_Scene_emitter_1"
        nodes = emit1.data.node_tree.nodes
        bb = nodes.new('ShaderNodeBlackbody')
        bb.inputs[0].default_value = 6200
        lf = nodes.new('ShaderNodeLightFalloff')
        lf.inputs[0].default_value = 175

        # add area lamp 2
        light_add(type='AREA')
        emit2 = bpy.context.active_object
        emit2.name = "Default_Scene_emitter_2"
        nodes = emit2.data.node_tree.nodes
        bb = nodes.new('ShaderNodeBlackbody')
        bb.inputs[0].default_value = 7200
        lf = nodes.new('ShaderNodeLightFalloff')
        lf.inputs[0].default_value = 160

        # add area lamp 3
        light_add(type='AREA')
        emit3 = bpy.context.active_object
        emit3.name = "Default_Scene_emitter_3"
        nodes = emit3.data.node_tree.nodes
        nodes["Emission"].inputs[0].default_value = (1, 1, 1, 1)
        nodes["Emission"].inputs[1].default_value = 100

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

        return emit1, emit2, emit3

    def viewCamera_animated(self):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = bpy.context.copy()
                override['area'] = area
                bpy.ops.view3d.viewnumpad(override, type = 'CAMERA')
                break

    def viewCamera(self):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break

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
