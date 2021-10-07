import bpy

class MSNAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Preferences for the addon")
        layout.operator("msn.install_dependencies", icon="CONSOLE")