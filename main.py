import bpy
import random
import string
import importlib
from . import rope_generator
from .rope_generator import GeneradorCuerdas



# Recarga los módulos durante el desarrollo
if "bpy" in locals():
    importlib.reload(rope_generator)
    
# Define la clase del operador
class MainOperator(bpy.types.Operator):
    bl_idname = "object.rope_generator"
    bl_label = "Generate Ropes"
    bl_description = "Papaya"
    
    def execute(self, context):
        props=context.scene.formulario
        tx_name = props.tx_name
        nu_grosor = props.nu_grosor
        generadorCuerdas=GeneradorCuerdas()
        
        print("¡Botón presionado!")
        
        # Generar texto aleatorio si está vacío
        if not tx_name.strip():
            tx_name = ''.join(random.choices(string.ascii_uppercase, k=5))
            props.tx_name = tx_name
        
        if nu_grosor <= 0:  # Si es nulo, vacío o menor o igual a 0
            nu_grosor = 0.04  # Restablecer a 0.04 metros
            props.nu_grosor = nu_grosor
        
        self.report({'INFO'}, f"Texto procesado: {tx_name} , {nu_grosor:.4f}")
        
        generadorCuerdas.inicialization(tx_name,nu_grosor)
        if generadorCuerdas.in_all_orden:
            generadorCuerdas.main()
        #self.report({'ERROR'}, "¡Ha ocurrido un error papaya!")
        self.report({'INFO'}, f"FINISHED")
        
        return {'FINISHED'}

class TestOperator(bpy.types.Operator):
    bl_idname = "object.test_hola"
    bl_label = "Prueba"
    bl_description = "Papaya 2"
    
    def execute(self, context):
        print("¡Botón presionado!")
        
        self.report({'INFO'}, f"Hola mundo")
        
        return {'FINISHED'}
    
# Registro de la clase
classes = [MainOperator,TestOperator]
    
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)