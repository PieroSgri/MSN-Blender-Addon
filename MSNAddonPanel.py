import bpy
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
   
class MSNAddonPanel(bpy.types.Panel):
    """Creates a Panel in the sidebar (N key, only in object mode)"""
    bl_label = "MSN Addon"
    bl_idname = "OBJECT_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "MSN Addon"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Import point cloud from pcd file
        layout.label(text="Import PCD file")
        row = layout.row()
        row.scale_y = 1.5
        row.operator("msn.import_point_cloud", icon="IMPORT")
        
        # Import and fill point cloud from pcd file
        layout.label(text="Import and fill PCD file")
        row = layout.row()
        row.scale_y = 1.5
        row.operator("msn.import_predict", icon="SCENE_DATA")
        
        """
        # Install Python dependencies
        layout.label(text="Install addon dependencies")
        row = layout.row()
        row.scale_y = 1.5
        row.operator("msn.install_dependencies", icon="CONSOLE")
        """