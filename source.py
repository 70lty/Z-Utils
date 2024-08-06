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

JIGGLEBONE_PRESETS = {
    "Cape / Jupe": '''$jigglebone "{name}"
{{
    is_flexible
    {{
        length 30
        tip_mass 0
        pitch_stiffness 50
        pitch_damping 7
        yaw_stiffness 50
        yaw_damping 7
        allow_length_flex
        along_stiffness 100
        along_damping 0
        angle_constraint 25.000001
    }}
}}''',
    "Cheveux": '''$jigglebone "{name}"
{{
    is_flexible
    {{
        length 30
        tip_mass 0
        pitch_stiffness 50
        pitch_damping 7
        yaw_stiffness 50
        yaw_damping 7
        allow_length_flex
        along_stiffness 100
        along_damping 0
        angle_constraint 30.000001
    }}
}}''',
    "Cape du Haut": '''$jigglebone "{name}"
{{
    is_flexible
    {{
        length 20
        tip_mass 50
        pitch_stiffness 100
        pitch_damping 20
        yaw_stiffness 100
        yaw_damping 15
        along_stiffness 100
        along_damping 0
        angle_constraint 25
    }}
}}''',
    "Queue": '''$jigglebone "{name}"
{{
    is_flexible
    {{
        length 20
        tip_mass 50
        pitch_stiffness 100
        pitch_damping 20
        yaw_stiffness 100
        yaw_damping 15
        along_stiffness 100
        along_damping 0
        angle_constraint 5
    }}
}}'''
}


class JiggleBoneQCOperator(bpy.types.Operator):
    bl_idname = "object.jiggle_bone_qc"
    bl_label = "JiggleBone QC"
    bl_description = "Generate a QC file for jiggle bones"

    preset: bpy.props.EnumProperty(
        name="Preset",
        description="Choose a jiggle bone preset",
        items=[
            ("Cape / Jupe", "Cape / Jupe", ""),
            ("Cheveux", "Cheveux", ""),
            ("Cape du Haut", "Cape du Haut", ""),
            ("Queue", "Queue", ""),
        ]
    )
    qc_file_name: bpy.props.StringProperty(name="QC File Name", description="Enter the name for the QC file", default="jiggle_bones")

    def execute(self, context):
        selected_bones = context.selected_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected")
            return {'CANCELLED'}

        preset_template = JIGGLEBONE_PRESETS.get(self.preset)
        if not preset_template:
            self.report({'ERROR'}, "Invalid preset selected")
            return {'CANCELLED'}

        default_folder = "C:/z_tools/z_utils/jiggleqc"
        if not os.path.exists(default_folder):
            os.makedirs(default_folder)
        
        file_path = os.path.join(default_folder, f"{self.qc_file_name}.qc")
        
        with open(file_path, 'a') as f:
            for bone in selected_bones:
                jigglebone_text = preset_template.format(name=bone.name)
                f.write(jigglebone_text + "\n")
                
                self.align_and_clear_bone_roll(bone)
        
        self.report({'INFO'}, f"JiggleBone QC file updated at: {file_path}")
        
        try:
            if os.name == 'nt':  
                os.startfile(file_path)
            elif os.name == 'posix': 
                subprocess.call(('open', file_path) if sys.platform == 'darwin' else ('xdg-open', file_path))
        except Exception as e:
            self.report({'ERROR'}, f"Unable to open file: {str(e)}")
        
        return {'FINISHED'}

    def align_and_clear_bone_roll(self, bone):
        bpy.ops.object.mode_set(mode='EDIT')
        bone.select = True
        bpy.context.view_layer.objects.active = bpy.context.object
        bpy.ops.armature.align()
        bone.roll = -3.14159  
        bpy.ops.object.mode_set(mode='POSE')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class ResetjiggleQCFilesOperator(bpy.types.Operator):
    bl_idname = "object.resetjiggle_qc_files"
    bl_label = "Reset QC Files"
    bl_description = "Delete all generated QC files"

    def execute(self, context):
        default_folder = "C:/z_tools/z_utils/jiggleqc"
        
        if os.path.exists(default_folder):
            for filename in os.listdir(default_folder):
                file_path = os.path.join(default_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.report({'ERROR'}, f"Failed to delete {file_path}. Reason: {e}")
                    return {'CANCELLED'}
        
        self.report({'INFO'}, "All QC files have been reset.")
        return {'FINISHED'}


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

        default_folder = "C:/z_tools/z_utils/animationqc"
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
    bl_idname = "object.resetanimation_qc_files"
    bl_label = "Reset QC Files"
    bl_description = "Delete all generated QC files"

    def execute(self, context):
        default_folder = "C:/z_tools/z_utils/animationqc"
        
        if os.path.exists(default_folder):
            for filename in os.listdir(default_folder):
                file_path = os.path.join(default_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.report({'ERROR'}, f"Failed to delete {file_path}. Reason: {e}")
                    return {'CANCELLED'}
        
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
        box.operator("object.resetanimation_qc_files", text="Reset all my QC Files")

        box = layout.box()
        box.label(text="Generate Collisions")
        box.operator("object.generate_collision_mesh", text="Generate Collision Mesh")

        box = layout.box()
        box.label(text="Jiggle Bone Tools")
        box.operator("object.jiggle_bone_qc", text="JiggleBone QC")
        box.operator("object.resetjiggle_qc_files", text="Reset all JiggleBone QC Files")

        box = layout.box()
        box.label(text=f"Toolkit Version ({toolkit_version})")
        box.label(text="Automatic update.")
        box.label(text="Plugin created by Zolty")

class GenerateCollisionMeshOperator(bpy.types.Operator):
    bl_idname = "object.generate_collision_mesh"
    bl_label = "Generate Collision Mesh"
    bl_description = "Automatically generate a collision mesh for the selected object"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        obj = context.object

        collision_mesh = obj.copy()
        collision_mesh.data = obj.data.copy()
        collision_mesh.name = f"{obj.name}_collision"

        for modifier in collision_mesh.modifiers:
            collision_mesh.modifiers.remove(modifier)

        context.collection.objects.link(collision_mesh)
        collision_mesh.select_set(True)
        context.view_layer.objects.active = collision_mesh

        self.report({'INFO'}, f"Collision mesh created for '{obj.name}'")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CreateAnimationQCOperator)
    bpy.utils.register_class(ResetQCFilesOperator)
    bpy.utils.register_class(ResetjiggleQCFilesOperator)
    bpy.utils.register_class(WeightPaintRightHandOperator)
    bpy.utils.register_class(WeightPaintLeftHandOperator)
    bpy.utils.register_class(ZToolkitMainPanel)
    bpy.utils.register_class(GenerateCollisionMeshOperator)
    bpy.utils.register_class(JiggleBoneQCOperator)

def unregister():
    bpy.utils.unregister_class(CreateAnimationQCOperator)
    bpy.utils.unregister_class(ResetQCFilesOperator)
    bpy.utils.unregister_class(ResetjiggleQCFilesOperator)
    bpy.utils.unregister_class(WeightPaintRightHandOperator)
    bpy.utils.unregister_class(WeightPaintLeftHandOperator)
    bpy.utils.unregister_class(ZToolkitMainPanel)
    bpy.utils.unregister_class(GenerateCollisionMeshOperator)
    bpy.utils.unregister_class(JiggleBoneQCOperator)


if __name__ == "__main__":
    register()