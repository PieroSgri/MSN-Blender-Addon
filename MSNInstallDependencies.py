import bpy
import subprocess
import sys
import os
from pathlib import Path

import logging
logging.basicConfig(level=logging.DEBUG)


def install(package):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package])
    except:
        string = package + " install failed."
        logging.debug(string)


def setup_py(module_path, root):
    os.chdir(module_path)
    subprocess.run([sys.executable, "setup.py", "install"])
    os.chdir(root)


class MSNInstallDependencies(bpy.types.Operator):
    """Install needed dependencies."""
    bl_idname = "msn.install_dependencies"
    bl_label = "Install dependencies"
    bl_description = ("Downloads and installs the required python packages for this add-on. "
                      "Internet connection is required. Blender may have to be started with "
                      "elevated permissions in order to install the package.")
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        
        bl_script_path = bpy.utils.script_paths()
        bl_script_path = Path(bl_script_path[1])
        
        logging.debug(f"Blender install dir scritps path: {bl_script_path}")
        
        sys.path.append(bl_script_path)
        sys.path.append(os.path.abspath(os.path.dirname(__file__)))
        
        requirements_path = Path(__file__).with_name("requirements.txt")
        requirements = []
        excluded = ["emd==0.0.0", "expansion-penalty==0.0.0", "mds==0.0.0"]
        specials = ["torch @ https://download.pytorch.org/whl/cu100/torch-1.2.0-cp37-cp37m-win_amd64.whl",
                    "torchvision @ https://download.pytorch.org/whl/cu100/torchvision-0.4.0-cp37-cp37m-win_amd64.whl"]
        
        
        current_path = Path(__file__).parent.resolve()
        
        emd_path = Path(os.path.join(current_path, "msnlib/emd/"))
        expansion_penalty_path = Path(os.path.join(current_path, "msnlib/expansion_penalty/"))
        MDS_path = Path(os.path.join(current_path, "msnlib/MDS/"))
        root_path = os.getcwd()
        
        try:
            #subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            with open(requirements_path, 'r') as f:
                for line in f:
                    line = str(line)
                    requirements.append(line)
                for pkg in requirements:
                    pkg = pkg.rstrip()
                    if pkg in excluded:
                        string = "Skipping package: " + pkg
                        logging.debug(string)
                        continue
                    if pkg in specials:
                        url = pkg.split(sep='@')
                        pkg = url[1].lstrip()

                    install(pkg)

            setup_py(emd_path, root_path)
            setup_py(expansion_penalty_path, root_path)
            setup_py(MDS_path, root_path)

        except (subprocess.CalledProcessError, ImportError) as err:
            return {"CANCELLED"}

        return{"FINISHED"}
