import bpy
from .main import MainOperator,TestOperator

# Define la clase para el panel
class MainPanel(bpy.types.Panel):
    bl_label = "Rope Generator Panel"
    bl_idname = "OBJECT_PT_rope_generator_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"
    
    @classmethod
    def poll(cls, context):
        # Verifica si el modo activo es 'POSE'
        return context.mode == 'POSE'
    
    
    def draw(self, context):
        layout = self.layout
        
        props=context.scene.formulario
        layout.prop(props, "tx_name", text="Rope name")
        layout.prop(props, "nu_grosor", text="Thickness")
        layout.operator("object.rope_generator")

        layout.operator("object.test_hola")
        

# Registro de la clase
classes = [MainPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)