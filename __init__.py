import bpy
import subprocess
import sys
import os
import importlib
from pathlib import Path

import logging
logging.basicConfig(level=logging.DEBUG)

bl_info = {
    "name": "MSN Point Cloud Completion",
    "author": "Piero Sgrignuoli, Luca Agostinelli",
    "description": "Point Cloud filling with MSN Point Cloud Completion",
    "blender": (2, 92, 0),
    "version": (1, 0, 0),
    "location": "",
    "warning": "",
    "category": "Generic"
}

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from .MSNInstallDependencies import MSNInstallDependencies
from .MSNAddonPreferences import MSNAddonPreferences
from .MSNImportPointCloud import MSNImportPointCloud
from .MSNImportPredict import MSNImportPredict
from .MSNAddonPanel import MSNAddonPanel

init_classes = (MSNInstallDependencies, MSNAddonPreferences)
classes = (MSNImportPointCloud, MSNImportPredict, MSNAddonPanel)


def register():
    
    try:
        for cls in init_classes:
            bpy.utils.register_class(cls)
            
        logging.debug("Init classes registered")
        
    except ModuleNotFoundError as err:
        logging.debug(f"Init classes not registered: {err}")
        
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
            
        logging.debug("Classes registered")
        
    except ModuleNotFoundError as err:
        logging.debug(f"Classes not registered, missing modules: {err}")

        

def unregister():
    
    try:
        for cls in init_classes:
            bpy.utils.unregister_class(cls)
            
        logging.debug("Init classes unregistered")
    
    except:
        logging.debug("Init classes not fully unregistered")
           
    try:
        for cls in classes:
            bpy.utils.unregister_class(cls)
            
        logging.debug("Classes unregistered")
        
    except:
        logging.debug("Classes not fully unregistered")

  
if __name__=="__main__":
    logging.debug("Registering classes")
    register()
