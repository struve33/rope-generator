import bpy

class Formulario(bpy.types.PropertyGroup):
    tx_name: bpy.props.StringProperty(
        name="Rope name",
        description="Nain name of the rope to generate",
        default="",
        maxlen=50
    )
    
    nu_grosor: bpy.props.FloatProperty(
        name="Rope thickness",
        description="Ropes's thickness",
        default=0.04,
        unit='LENGTH',
        precision=4
    )