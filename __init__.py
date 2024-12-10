import bpy
import importlib
from . import main, ui,form,rope_generator
from .form import Formulario


bl_info = {
    "name": "Rope Generator",
    "description": "A rope generator with clothing physics and manual adjustment.",
    "author": "Alberto Jose Struve Torres",
    "version": (0, 5),
    "blender": (4, 3, 0),
    "category": "Object",
}

# Recarga los módulos durante el desarrollo
if "bpy" in locals():
    importlib.reload(main)
    importlib.reload(ui)
    importlib.reload(form)
    importlib.reload(rope_generator)
    




def register():
    bpy.utils.register_class(Formulario)
    bpy.types.Scene.formulario = bpy.props.PointerProperty(type=Formulario)
    main.register()  # Llama al registro del módulo `core`
    ui.register()    # Llama al registro del módulo `ui`

def unregister():
    ui.unregister()
    main.unregister()
    del bpy.types.Scene.formulario
    bpy.utils.unregister_class(Formulario)
    
    
if __name__ == "__main__":
    register()