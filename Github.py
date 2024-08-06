#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Filename: c:\Users\zolty\source\Github\Z-Utils\Github.py
# Path: c:\Users\zolty\source\Github\Z-Utils
# Created Date: Wednesday, July 31st 2024, 3:29:29 pm
# Author: Zolty
# 
# Copyright (c) 2024 SDA
###

bl_info = {
    "name": "Z-Utils Github",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "description": "Télécharge et exécute le script Z-Utils",
    "author": "Zolty",
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
}

import requests
import bpy

GITHUB_URL = "https://raw.githubusercontent.com/70lty/Z-Utils/main/source.py"

def download_and_execute_script():
    try:
        print("Téléchargement du script depuis GitHub...")
        response = requests.get(GITHUB_URL)
        response.raise_for_status()
        script_content = response.text
        print("Script téléchargé avec succès.")
        code = compile(script_content, "<string>", "exec")
        print("Exécution du script...")
        exec(code, {'__name__': '__main__'})
        print("Script exécuté avec succès.")
    except requests.RequestException as e:
        error_message = f"Erreur lors de la récupération du script : {e}"
        print(error_message)
        raise Exception(error_message)
    except Exception as e:
        error_message = f"Erreur lors de l'exécution du script : {e}"
        print(error_message)
        raise Exception(error_message)

class Z_Utils_OT_UpdateFromGitHub(bpy.types.Operator):
    bl_idname = "object.z_utils_update_from_github"
    bl_label = "Z-Utils loading with GitHub"
    bl_description = "Télécharge et exécute le script Z-Utils depuis GitHub"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            download_and_execute_script()
            self.report({'INFO'}, "Script Z-Utils mis à jour et exécuté avec succès")
        except Exception as e:
            self.report({'ERROR'}, f"Erreur lors de la mise à jour du script : {e}")
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(Z_Utils_OT_UpdateFromGitHub)

def unregister():
    bpy.utils.unregister_class(Z_Utils_OT_UpdateFromGitHub)

if __name__ == "__main__":
    register()
