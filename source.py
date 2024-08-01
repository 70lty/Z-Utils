#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Filename: c:\Users\zolty\source\Github\Z-Utils\Z-Utils\source.py
# Path: c:\Users\zolty\source\Github\Z-Utils\Z-Utils
# Created Date: Thursday, August 1st 2024, 3:36:31 am
# Author: Zolty
# 
# Copyright (c) 2024 SDA
###
bl_info = {
    "name": "Z-Utils Blender",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "description": "Script open source",
    "author": "Zolty",
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
}

import bpy
import os
import subprocess
import tempfile
import webbrowser
import requests

toolkit_version = "1.2"
DICT_URL = "https://raw.githubusercontent.com/70lty/Z-Utils/main/bones.txt"

bone_mappings = {}

class WeightPaintOperator(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}
    
    def weight_paint(self, context, target_bone_name):
        obj = context.object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}

        armature = None
        for ob in bpy.context.scene.objects:
            if ob.type == 'ARMATURE' and target_bone_name in ob.data.bones:
                armature = ob
                break

        if not armature:
            self.report({'ERROR'}, f"No armature found with the bone '{target_bone_name}'")
            return {'CANCELLED'}

        target_bone = armature.data.bones.get(target_bone_name)
        if not target_bone:
            self.report({'ERROR'}, f"Bone '{target_bone_name}' not found in the armature")
            return {'CANCELLED'}


        if target_bone_name not in obj.vertex_groups:
            vg = obj.vertex_groups.new(name=target_bone_name)
        else:
            vg = obj.vertex_groups[target_bone_name]


        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.vertex_group_assign()
        bpy.ops.object.mode_set(mode='OBJECT')
        

        obj.vertex_groups.active = vg
        self.report({'INFO'}, f"Object weight painted on '{target_bone_name}'")
        return {'FINISHED'}

class WeightPaintRightHandOperator(WeightPaintOperator):
    bl_idname = "object.weight_paint_right_hand"
    bl_label = "Weight Paint to Right Hand"
    bl_description = "Weight paint the model to the right hand"

    def execute(self, context):
        return self.weight_paint(context, "ValveBiped.Bip01_R_Hand")

class WeightPaintLeftHandOperator(WeightPaintOperator):
    bl_idname = "object.weight_paint_left_hand"
    bl_label = "Weight Paint to Left Hand"
    bl_description = "Weight paint the model to the left hand"

    def execute(self, context):
        return self.weight_paint(context, "ValveBiped.Bip01_L_Hand")


class CreateAnimationQCOperator(bpy.types.Operator):
    bl_idname = "object.create_animation_qc"
    bl_label = "Create Animation QC"
    bl_description = "Generate or update a QC file for animations"

    animation_path: bpy.props.StringProperty(name="Animation Path", description="Enter the path for the animations", default="")
    qc_file_name: bpy.props.StringProperty(name="QC File Name", description="Enter the name for the QC file", default="")
    include_all_animations: bpy.props.StringProperty(name="Include All Animations (Y/N)", description="Include all animations (Y) or only selected (N)", default="Y")

    def execute(self, context):
        armature = context.object

        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected or selected object is not an armature")
            return {'CANCELLED'}

        if self.include_all_animations.strip().upper() == "Y":
            animations = [action for action in bpy.data.actions]
        elif self.include_all_animations.strip().upper() == "N":
            animations = [context.object.animation_data.action] if context.object.animation_data and context.object.animation_data.action else []
        else:
            self.report({'ERROR'}, "Invalid input for including animations. Use 'Y' for all animations or 'N' for only selected animation.")
            return {'CANCELLED'}
        
        if not animations:
            self.report({'ERROR'}, "No animations found")
            return {'CANCELLED'}

        default_folder = "C:/z_tools/z_utils/"
        if not os.path.exists(default_folder):
            os.makedirs(default_folder)
        
        file_path = os.path.join(default_folder, f"{self.qc_file_name}.qc")
        
        if bpy.data.filepath:
            project_folder = os.path.dirname(bpy.data.filepath)
            file_path = os.path.join(project_folder, f"{self.qc_file_name}.qc")
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        animation_template = (
            '$sequence "{anim_name}" {{\n'
            '    "{anim_path}/{anim_name}.smd"\n'
            '    activity "ZUtils" 1\n'
            '    fadein 0.2\n'
            '    fadeout 0.2\n'
            '    snap\n'
            '    fps 30\n'
            '}}\n'
        )

        existing_animations = set()
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                existing_animations = {line.split('"')[1] for line in f if line.strip().startswith('$sequence')}
        
        with open(file_path, 'a') as f:
            for anim in animations:
                anim_name = anim.name.replace(" ", "_")
                if anim_name not in existing_animations:
                    f.write(animation_template.format(anim_name=anim_name, anim_path=self.animation_path).strip() + "\n")
        
        self.report({'INFO'}, f"Animation QC file created/updated at: {file_path}")
        
        try:
            if os.name == 'nt':  
                os.startfile(file_path)
            elif os.name == 'posix': 
                subprocess.call(('open', file_path) if sys.platform == 'darwin' else ('xdg-open', file_path))
        except Exception as e:
            self.report({'ERROR'}, f"Unable to open file: {str(e)}")
        
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class ResetQCFilesOperator(bpy.types.Operator):
    bl_idname = "object.reset_qc_files"
    bl_label = "Reset QC Files"
    bl_description = "Delete all generated QC files"

    def execute(self, context):
        default_folder = "C:/z_tools/z_utils/"
        
        if os.path.exists(default_folder):
            for filename in os.listdir(default_folder):
                if filename.endswith(".qc"):
                    file_path = os.path.join(default_folder, filename)
                    os.remove(file_path)
        
        self.report({'INFO'}, "All QC files have been reset.")
        return {'FINISHED'}

class ZToolkitMainPanel(bpy.types.Panel):
    bl_label = "Z Toolkit"
    bl_idname = "Z_Toolkit_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Z Toolkit'
    
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Model Attachment")
        box.operator("object.weight_paint_right_hand")
        box.operator("object.weight_paint_left_hand")
        
        box = layout.box()
        box.label(text="Animation Tools")
        box.operator("object.create_animation_qc")
        box.operator("object.reset_qc_files", text="Reset all my QC Files")

        box = layout.box()
        box.label(text=f"Toolkit Version ({toolkit_version})")
        box.label(text="Automatic update.")
        box.label(text="Plugin created by Zolty")

def register():
    bpy.utils.register_class(CreateAnimationQCOperator)
    bpy.utils.register_class(ResetQCFilesOperator)
    bpy.utils.register_class(WeightPaintRightHandOperator)
    bpy.utils.register_class(WeightPaintLeftHandOperator)
    bpy.utils.register_class(ZToolkitMainPanel)

def unregister():
    bpy.utils.unregister_class(CreateAnimationQCOperator)
    bpy.utils.unregister_class(ResetQCFilesOperator)
    bpy.utils.unregister_class(WeightPaintRightHandOperator)
    bpy.utils.unregister_class(WeightPaintLeftHandOperator)
    bpy.utils.unregister_class(ZToolkitMainPanel)

if __name__ == "__source__":
    register()