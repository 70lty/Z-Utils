#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Filename: c:\Users\zolty\source\Github\Z-Utils\main.py
# Path: c:\Users\zolty\source\Github\Z-Utils
# Created Date: Wednesday, July 31st 2024, 3:29:42 pm
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

script_version = "1.2"
BONES_URL = "https://raw.githubusercontent.com/70lty/Z-Utils/main/bones.txt"

bone_rename_mapping = {}

def download_rename_dictionaries():
    try:
        response = requests.get(BONES_URL)
        response.raise_for_status()
        exec(response.text, globals())
    except requests.RequestException as e:
        raise Exception(f"Error fetching rename dictionaries: {e}")

download_rename_dictionaries()

class BoneRenamerOperator(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}

    def rename_bones(self, context, rename_dict):
        armature = context.object
        if armature and armature.type == 'ARMATURE':
            bpy.ops.object.mode_set(mode='EDIT')
            for bone in armature.data.edit_bones:
                if bone.name in rename_dict:
                    bone.name = rename_dict[bone.name]
            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'INFO'}, "Bones successfully renamed")
        else:
            self.report({'ERROR'}, "Selected object is not an armature or no object selected")

class RenameBonesBCOperator(BoneRenamerOperator):
    bl_idname = "object.rename_bones_bc"
    bl_label = "BC Mobile"
    bl_description = "Rename bones for Black Clover Mobile models"

    def execute(self, context):
        self.rename_bones(context, bones_rename_dict)
        return {'FINISHED'}

class RenameBonesJFOperator(BoneRenamerOperator):
    bl_idname = "object.rename_bones_jf"
    bl_label = "Jump Force"
    bl_description = "Rename bones for Jump Force models"

    def execute(self, context):
        self.rename_bones(context, bones_rename_dict6)
        return {'FINISHED'}

class RenameBonesXPSOperator(BoneRenamerOperator):
    bl_idname = "object.rename_bones_xps"
    bl_label = "XPS Models"
    bl_description = "Rename bones for XPS models"

    def execute(self, context):
        self.rename_bones(context, bones_rename_dict2)
        return {'FINISHED'}

class RenameBonesXPS2Operator(BoneRenamerOperator):
    bl_idname = "object.rename_bones_xps2"
    bl_label = "XPS 2 Models"
    bl_description = "Rename bones for XPS 2 models"

    def execute(self, context):
        self.rename_bones(context, bones_rename_dict3)
        return {'FINISHED'}

class RenameBonesNRTOperator(BoneRenamerOperator):
    bl_idname = "object.rename_bones_nrt"
    bl_label = "Shinobi Striker"
    bl_description = "Rename bones for Naruto: Shinobi Striker models"

    def execute(self, context):
        self.rename_bones(context, bones_rename_dict5)
        return {'FINISHED'}

class CreateJigglebonesQCOperator(bpy.types.Operator):
    bl_idname = "object.create_jigglebones_qc"
    bl_label = "Jigglebones QC"
    bl_description = "Create a z_utils_jigglebones.qc file with jigglebones for selected bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object
        selected_bones = [bone.name for bone in context.selected_bones]

        if not selected_bones:
            self.report({'ERROR'}, "No bones selected")
            return {'CANCELLED'}

        default_folder = "C:/z_utils/"
        if not os.path.exists(default_folder):
            os.makedirs(default_folder)
        
        file_path = os.path.join(default_folder, "z_utils_jigglebones.qc")
        
        if bpy.data.filepath:
            project_folder = os.path.dirname(bpy.data.filepath)
            file_path = os.path.join(project_folder, "z_utils_jigglebones.qc")
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        jigglebone_template = (
            '$jigglebone "{bone_name}"\n'
            '{{\n'
            '    is_flexible\n'
            '    {{\n'
            '        length 40\n'
            '        tip_mass 0\n'
            '        pitch_stiffness 50\n'
            '        pitch_damping 7\n'
            '        yaw_stiffness 50\n'
            '        yaw_damping 7\n'
            '        allow_length_flex\n'
            '        along_stiffness 100\n'
            '        along_damping 0\n'
            '        angle_constraint 30.000001\n'
            '    }}\n'
            '}}\n'
        )
        
        with open(file_path, 'w') as f:
            for bone_name in selected_bones:
                f.write(jigglebone_template.format(bone_name=bone_name).strip() + "\n")
        
        self.report({'INFO'}, f"File created at: {file_path}")
        
        try:
            if os.name == 'nt':  
                os.startfile(file_path)
            elif os.name == 'posix': 
                subprocess.call(('open', file_path) if sys.platform == 'darwin' else ('xdg-open', file_path))
        except Exception as e:
            self.report({'ERROR'}, f"Unable to open file: {str(e)}")
        
        return {'FINISHED'}

class SetBoneRollOperator(bpy.types.Operator):
    bl_idname = "object.set_bone_roll"
    bl_label = "Bone Roll -180"
    bl_description = "Set the roll of selected bones to -180"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object

        if armature and armature.type == 'ARMATURE':
            bpy.ops.object.mode_set(mode='EDIT')  
            for bone in armature.data.edit_bones:
                if bone.select: 
                    bone.roll = -180 
            bpy.ops.object.mode_set(mode='OBJECT')  
            self.report({'INFO'}, "Roll of selected bones set to -180")
        else:
            self.report({'ERROR'}, "No armature selected or selected object is not an armature")
        
        return {'FINISHED'}

def save_bone_names(filepath):
    armature = bpy.context.object
    if armature and armature.type == 'ARMATURE':
        with open(filepath, 'w') as file:
            for bone in armature.data.bones:
                file.write(f"{bone.name}\n")
        print(f"Bone names saved to {filepath}")
    else:
        print("No armature selected or selected object is not an armature")

class SaveBoneNamesOperator(bpy.types.Operator):
    bl_idname = "object.save_bone_names"
    bl_label = "Save Bone Names"
    bl_description = "Save bone names to a text file and open it automatically"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        filepath = os.path.join(os.path.expanduser('~'), 'z_utils_bonenames.txt')
        save_bone_names(filepath)
        webbrowser.open(filepath)
        return {'FINISHED'}

class MergeWeightsOperatorBase(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}

    def merge_weights(self, context, filter_func):
        armature = context.object
        bones_to_merge = []

        if armature and armature.type == 'ARMATURE':
            bones_to_merge = [bone for bone in armature.data.bones if filter_func(bone)]

            bpy.ops.object.mode_set(mode='EDIT')
            for bone in bones_to_merge:
                parent = bone.parent
                if parent:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.context.view_layer.objects.active = armature
                    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                    bpy.ops.object.vertex_group_transfer_weight()
                    bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.001, keep_single=False)
                    bpy.ops.object.vertex_group_normalize_all()
                    bpy.ops.object.mode_set(mode='EDIT')
                    armature.data.edit_bones.remove(bone)

            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'INFO'}, "Weights successfully merged")
        else:
            self.report({'ERROR'}, "No armature selected or selected object is not an armature")

class MergeWeightsSelectedOperator(MergeWeightsOperatorBase):
    bl_idname = "object.merge_weights_selected"
    bl_label = "Merge Weights (Selected)"
    bl_description = "Merge weights of selected bones in the armature"

    def execute(self, context):
        self.merge_weights(context, lambda bone: bone.select)
        return {'FINISHED'}

class MergeWeightsAllOperator(MergeWeightsOperatorBase):
    bl_idname = "object.merge_weights_all"
    bl_label = "Merge Weights (All)"
    bl_description = "Merge weights of all unnecessary bones in the armature"

    def execute(self, context):
        self.merge_weights(context, lambda bone: "ValveBiped" in bone.name)
        return {'FINISHED'}

class MoveAndWeightPaintOperator(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}
    
    def move_and_weight_paint(self, context, target_bone_name):
        obj = context.object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}

        armature = None
        for ob in bpy.context.scene.objects:
            if ob.type == 'ARMATURE':
                if target_bone_name in ob.data.bones:
                    armature = ob
                    break

        if not armature:
            self.report({'ERROR'}, "No armature found with the specified bone")
            return {'CANCELLED'}

        target_bone = armature.data.bones.get(target_bone_name)
        if not target_bone:
            self.report({'ERROR'}, f"Target bone '{target_bone_name}' not found")
            return {'CANCELLED'}

        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        obj.select_set(True)
        armature.data.bones.active = target_bone
        bpy.ops.object.parent_set(type='BONE', keep_transform=True)
        obj.parent_bone = target_bone_name

        # Weight paint
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        if target_bone_name not in obj.vertex_groups:
            vg = obj.vertex_groups.new(name=target_bone_name)
        else:
            vg = obj.vertex_groups[target_bone_name]
        bpy.ops.object.vertex_group_set_active(group=vg.index)
        bpy.ops.object.vertex_group_assign()

        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, f"Object moved to and weight painted on '{target_bone_name}'")
        return {'FINISHED'}

class MoveAndWeightPaintRightOperator(MoveAndWeightPaintOperator):
    bl_idname = "object.move_weight_paint_right"
    bl_label = "WorldModel Right"
    bl_description = "Move and weight paint the model on the right hand"

    def execute(self, context):
        return self.move_and_weight_paint(context, "ValveBiped.Bip01_R_Hand")

class MoveAndWeightPaintLeftOperator(MoveAndWeightPaintOperator):
    bl_idname = "object.move_weight_paint_left"
    bl_label = "WorldModel Left"
    bl_description = "Move and weight paint the model on the left hand"

    def execute(self, context):
        return self.move_and_weight_paint(context, "ValveBiped.Bip01_L_Hand")

class ZUtilsMainPanel(bpy.types.Panel):
    bl_label = "Z-Utils Tools"
    bl_idname = "Z_Utils_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Z-Utils'
    
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Your Armature")
        box.operator("object.save_bone_names")
        box.operator("object.merge_weights_selected", text="Merge Weights (Selected)")
        box.operator("object.merge_weights_all", text="Merge Weights (All)")

        box = layout.box()
        box.label(text="Rename Bones")
        box.operator("object.rename_bones_bc")
        box.operator("object.rename_bones_nrt")
        box.operator("object.rename_bones_jf")
        box.operator("object.rename_bones_xps")
        box.operator("object.rename_bones_xps2")
       
        box = layout.box()
        box.label(text="Create Jigglebones QC")
        box.operator("object.create_jigglebones_qc")
        box.operator("object.set_bone_roll")

        box = layout.box()
        box.label(text="WorldModel")
        box.operator("object.move_weight_paint_right")
        box.operator("object.move_weight_paint_left")
        
        box = layout.box()
        box.label(text=f"Update Script ({script_version})")
        box.label(text="Update is handled separately in Github.py")
        box.label(text="Plugin created by Zolty")

def register():
    bpy.utils.register_class(SaveBoneNamesOperator)
    bpy.utils.register_class(RenameBonesNRTOperator)
    bpy.utils.register_class(RenameBonesJFOperator)
    bpy.utils.register_class(RenameBonesBCOperator)
    bpy.utils.register_class(RenameBonesXPSOperator)
    bpy.utils.register_class(RenameBonesXPS2Operator)
    bpy.utils.register_class(SetBoneRollOperator)
    bpy.utils.register_class(CreateJigglebonesQCOperator)
    bpy.utils.register_class(MergeWeightsSelectedOperator)
    bpy.utils.register_class(MergeWeightsAllOperator)
    bpy.utils.register_class(MoveAndWeightPaintRightOperator)
    bpy.utils.register_class(MoveAndWeightPaintLeftOperator)
    bpy.utils.register_class(ZUtilsMainPanel)

def unregister():
    bpy.utils.unregister_class(SaveBoneNamesOperator)
    bpy.utils.unregister_class(RenameBonesNRTOperator)
    bpy.utils.unregister_class(RenameBonesJFOperator)
    bpy.utils.unregister_class(RenameBonesBCOperator)
    bpy.utils.unregister_class(RenameBonesXPSOperator)
    bpy.utils.unregister_class(RenameBonesXPS2Operator)
    bpy.utils.unregister_class(SetBoneRollOperator)
    bpy.utils.unregister_class(CreateJigglebonesQCOperator)
    bpy.utils.unregister_class(MergeWeightsSelectedOperator)
    bpy.utils.unregister_class(MergeWeightsAllOperator)
    bpy.utils.unregister_class(MoveAndWeightPaintRightOperator)
    bpy.utils.unregister_class(MoveAndWeightPaintLeftOperator)
    bpy.utils.unregister_class(ZUtilsMainPanel)

if __name__ == "__main__":
    register()