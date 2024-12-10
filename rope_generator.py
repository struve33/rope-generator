import bpy
import mathutils
import re
from pprint import pprint
# Obtener el objeto activo (asegúrate de que sea un Armature)
#obj = bpy.context.object


class GeneradorCuerdas:
    objeto=None
    esqueleto=None
    esqueleto_edit=None
    core_bone=None
    tx_core_bone_name=''
    tx_collecion_fisica=''
    nu_grosor=0.04
    
    bone_pose_selected=None
    bone_edit_selected=None

    lista_huesos_fk=None
    lista_huesos_physic=None
    lista_huesos_parent=None
    
    tx_bcoll_name=''
    lista_bcoll_name=[]
    
    #Esto relacionara los huesos en las diferentes estructuras (FK, physic, parent)
    obj_vinculos_bones={}
    
    bcoll_main=None
    bcoll_FK=None
    bcoll_physic=None
    bcoll_parent=None
    
    tx_bcoll_main=''
    
    lista_mallas_fisica=[]
    lista_before_bcoll=[]
    
    
    #Esto va ser contenedor de todas las tiras
    """
        las tiras ban a ser grupos de huesos y mallas... tiras o cuerdas
        
        una tira contendra un conjusto de huesos FK,fisica y parent relacionados
        asi como tambien un objeto-malla.
        
    """
    lista_tiras=[]
    
    in_all_orden=False
    
    def __init__(self)->None:
        pass
        """Constructor"""
        """self.objeto=bpy.context.object
        
        if not self.check_armature():
            print("error en armature")
            return
        
        self.esqueleto=self.objeto.data
        self.lista_huesos_fk= [bone for bone in self.esqueleto.bones if bone.select]
        
        self.tx_bcoll_name='cuerdas'
        self.tx_core_bone_name='root'
        
        filtro=[bone.name for bone in self.esqueleto.bones if bone.name=='root']
        core_bone=filtro[0]
        
        self.in_all_orden=True
        print("iniciado")"""
    
    def report(self, level, message):
        # Esto sería un wrapper que puede llamarse en cualquier parte de tu clase
        bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=message), title="Alerta", icon='INFO' if level == 'INFO' else 'ERROR')
        print(f"[{level}] {message}")
    


    def inicialization(self,_tx_name:str,_nu_grosor:float)->None:
        
        #PASO 1 CHEQUEAR OBJETO SELECCIONADO
        if not self.check_armature():
            print("error en armature")
            return
        
        #PASO 2 INICIALIZAR VARIABLES GENERALES
        self.objeto=bpy.context.object
        self.esqueleto=self.objeto.data 
        self.lista_huesos_fk= [bone for bone in self.esqueleto.bones if bone.select]
        self.bone_pose_selected=[bone for bone in bpy.context.selected_pose_bones] #self.lista_huesos_fk
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            armature_edit=bpy.context.object.data
            self.bone_edit_selected=[bone for bone in armature_edit.edit_bones if bone.select]
            bpy.ops.object.mode_set(mode='POSE')
        except Exception as e:
            print(e)

        self.tx_bcoll_name=_tx_name
        self.nu_grosor=_nu_grosor
        self.lista_before_bcoll.append(_tx_name)
        #print(self.lista_huesos_fk)
        #PASO 3 BUSCAR HUESO NUCLEO O ANCLA
        """
            Basicamente se busca un hueso de origen que sirva de ancla a las tiras
            que se van a formar, es importante que sea solo un hueso ya que asi es 
            como trabaja este proceso, con solo un hueso de origen.
            
            El proceso de abajo primero selecciona los primeros huesos que forman 
            las tiras, luego selecciona el primer hueso origen de la lista, y finalmente
            chequea si ese hueso se mantiene.
        """
        pprint(self.bone_pose_selected)
        lista_origen=[bone for bone in self.bone_pose_selected if not bone.parent or bone.parent not in self.bone_pose_selected]
        root_bone=lista_origen[0].parent
        #print(root_bone)
        if root_bone is None:
            self.report({'ERROR'}, f"There must be a bone of origin/father")
            return
        
        in_multiple_root_bone=False
        
        for bone in lista_origen:
            if bone.parent!=root_bone:
                #print(bone.parent,root_bone)
                in_multiple_root_bone=True
                continue
        
        if in_multiple_root_bone:
            self.report({'ERROR'}, f"There should only be one bone of origin")
            return
        
        self.tx_core_bone_name=root_bone.name
        self.core_bone=root_bone
        
        #[bone.name for bone in self.bcoll_FK.bones if not bone.parent or bone.parent not in lista_bcoll_FK_all]
        
        
        
        #PASO 4 FINAL
        self.in_all_orden=True
    
    #-----------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------
    #*********************************************************MAIN****************************************
    #-----------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------   
    def main(self)->None:
        """
            Este es el metodo principal encargado de generar y ejecutar todo
        """
        if not self.in_all_orden:
            print("No se pudo ejecutar por una inicialización incompleta")
            self.report({'ERROR'}, f"The process could not be executed because there was incomplete initialization")
            return
        
        #PASO 0 BORRAR POR CAMBIO DE NOMBRE
        if len(self.lista_before_bcoll)>1:
            self.delete_all_before()
        
        #PASO 1 - RENOMBRAR LOS HUESOS SELECCIONADOS
        self.rename_inicial()
        
        #PASO 2 - GENERAR BONE COLLECTIONS
        self.generar_grupos()
        
        #PASO 3 - GENERAR LOS HUESOS PARA LAS COLLECCIONES
        self.generar_estructuras_huesos()
        
        #PASO 4 - GENERAR LAS TIRAS O CUERDAS
        self.generar_tiras()
        
        #PASO 5 - GENERAR MALLAS DE LAS TIRAS FISICAS
        self.generar_cuerdas_fisicas()
        
        #PASO 6 - APLICAR MODIFICADORES Y FISICAS
        self.set_modificadores()
        
        
        
  
        
        
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #****************************GESTION*************************************
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------   
    def generar_estructuras_huesos(self)->None:
        """
            Este metodo se encarga de manejar los procesos que generaran
            los conjuntos de huesos.
        """
    
        lista_huesos = [bone for bone in self.esqueleto.bones if bone.select]
    
        #PASO 1 AGRUPAR LOS HUESOS REALES-FK
        for hueso in lista_huesos:
            self.bcoll_FK.assign(hueso)
    
        self.remove_collections(lista_huesos,self.bcoll_FK.name)
        print('PASO 3.1 agrupar huesos reales a fk: completado')
    
        #PASO 2 GENERAR HUESOS DE FISICA
        self.generar_huesos_fisica()
        print('PASO 3.2 generar huesos fisicos y agruparlos: completado')
        
        
        #PASO 3 GENERAR HUESOS DE PARENT
        self.generar_huesos_parent()
        print('PASO 3.3 generar huesos parent y agruparlos: completado')
        #print(self.obj_vinculos_bones)
    
    def generar_cuerdas_fisicas(self)->None:
        """
            Este metodo se encarga de manejar los procesos que generaran
            los conjuntos de objetos que representaran las tiras fisicas.
        """
        
        
        #PASO 1 GENERAR COLLECCION.
        self.make_colleccion_fisica()
        
        #PASO 2 GENERAR EL OBJETO INICIAL.
        self.generar_mallas_fisicas()
        
        #PASO 3 AJUSTAR LAS CUERDAS; DARLE VOLUMEN.
        self.set_cuerdas_volumen()
        
        #PASO 4 CREAR LOS VERTEX GROUP DE LA MALLA Y DARLE PESOS.
        self.set_vertex_groups()
        
        print("PASO 5 generar objetos fisicos: completado.") 
    
    
    
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #******************************GETTERS***********************************
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------   
    def check_bone_edit(self,_bone:object)->bool:
        return ((bpy.context.mode == 'POSE' and _bone.select) or (bpy.context.mode == 'EDIT_ARMATURE') and _bone.select)
    
    
    
    def check_armature(self)->bool:
        
        if bpy.context.mode != 'POSE':
            self.report({'ERROR'}, f"User is not in 'POSE' mode")
            return False
        
        
        objeto=None
        
        selected_objects = bpy.context.selected_objects
        
        # Verificar si hay huesos seleccionados en el modo POSE
        selected_bones = bpy.context.selected_pose_bones
        if len(selected_bones)<=0:
            self.report({'ERROR'}, f"You must have bones selected")
            return False

        #print('papaya:',selected_objects)
        
        
        #VERIFICAR SI HAY UNA ARMATURE SELECCIONADO
        if len(selected_objects)>1:
            self.report({'ERROR'}, f"You must have only one object selected")
            return False
        
        if len(selected_objects)<=0 and len(selected_bones)>0:
            objeto = bpy.context.object
            objeto.select_set(True)
            
        elif len(selected_objects)>0:  
            objeto=selected_objects[0]
          
        else:
            self.report({'ERROR'}, f"You must have only one object selected")
            return False
        
        
            
        if objeto.type != 'ARMATURE':
            self.report({'ERROR'}, f"The object most be a 'ARMATURE' type")
            return False
        
        return True
    
    def get_cadena(self,tx_hueso_origen:str)->list:
        lista_nodos = []
        
        
        bpy.ops.object.mode_set(mode='POSE')
        bone = self.esqueleto.bones.get(tx_hueso_origen)
        while bone:
            lista_nodos.append(bone.name)
            # Obtener el primer hijo (si existe)
            if bone.children:
                bone = bone.children[0]  # Tomar el primer hijo
            else:
                bone = None  # No hay más descendientes
        
        return lista_nodos
    
    def check_bcoll_exist(self,_tx_name:str)->bool:

        def buscar_bcoll(bcoll,__tx_name):
            if bcoll.name == __tx_name:
                return True
            # Buscar recursivamente en las subcolecciones
            for subcollection in bcoll.children:
                if buscar_bcoll(subcollection, __tx_name):
                    return True
                
            return False

        # Obtener las colecciones de huesos de la armadura
        root_collections = self.esqueleto.collections_all
        for root_collection in root_collections:
            if buscar_bcoll(root_collection, _tx_name):
                return True
        
        return False

    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #******************************SETTERS***********************************
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    
    
    def rename_inicial(self):
        # Iterar sobre los huesos seleccionados
        for bone in self.lista_huesos_fk:
            if self.check_bone_edit(bone):
                # Separar el nombre y el sufijo numérico (si lo tiene)
                name_parts = bone.name.rsplit('.', 1)
            
                if len(name_parts) == 2 and name_parts[1].isdigit():
                    if '_FK' == name_parts[0][-3:]:
                        # Si no tiene sufijo numérico
                        new_name = bone.name
                    else:
                        # Si el nombre tiene un sufijo numérico
                        new_name = f"{name_parts[0]}_FK.{name_parts[1]}"
                
                else:
                    if '_FK' == bone.name[-3:]:
                        # Si no tiene sufijo numérico
                        new_name = bone.name
                    else:
                        # Si no tiene sufijo numérico
                        new_name = f"{bone.name}_FK"
            
                # Renombrar el hueso
                bone.name = new_name
    
        print("PASO 1 Renombrado: completado.") 
    
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def set_cuerdas_volumen(self)->None:
        """
            Este a traves de un bucle le asignara un volumen a las
            mallas de las cuerdas.
        """
        for item in self.lista_tiras:   
            self.set_cuerda_volumen(item['tx_objeto_name']) 
        
        print("PASO 5.3 Asignar volumen: completado.") 
    
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def set_cuerda_volumen(self,_tx_name,_nu_resolution=0)->None:
        """
            Este ahora si de manera individual asignara un volumen a
            una malla.
        """
        bpy.ops.object.mode_set(mode='OBJECT')
        obj_tira = bpy.data.objects.get(_tx_name)
        
        # Convertir a curva
        bpy.ops.object.select_all(action='DESELECT')
        obj_tira.select_set(True)
        bpy.context.view_layer.objects.active = obj_tira
        bpy.ops.object.convert(target='CURVE')
        
        # Ajustar propiedades de la curva
        obj_tira.data.fill_mode = 'FULL'
        obj_tira.data.bevel_depth = self.nu_grosor
        obj_tira.data.bevel_resolution = _nu_resolution
        
        # Volver a convertir en objeto
        bpy.ops.object.convert(target='MESH')
        
        
        # Volver al modo pose con el armature seleccionado
        bpy.ops.object.select_all(action='DESELECT')
        self.objeto.select_set(True)
        bpy.context.view_layer.objects.active = self.objeto
        
        
        bpy.ops.object.mode_set(mode='POSE')
        
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def set_vertex_groups(self)->None:
        """
            Este a traves de un bucle le asignara los vertex groups y sus 
            pesos
        """
        for item in self.lista_tiras:   
            self.set_vertex_group(item) 
        
        print("PASO 5.4 Asignar vertex group: completado.") 
          
      
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def set_vertex_group(self,_objeto:object)->None:
        """
            Este ahora si de manera individual asignara un volumen a
            una malla.
        """  
        
        #PASO 1 seleccionar objeto
        bpy.ops.object.mode_set(mode='OBJECT')
        obj_tira = bpy.data.objects.get(_objeto['tx_objeto_name'])
        
        bpy.ops.object.select_all(action='DESELECT')
        obj_tira.select_set(True)
        bpy.context.view_layer.objects.active = obj_tira
        #bpy.ops.object.mode_set(mode='EDIT')
        
        # Obtener la malla y las posiciones de los vértices
        mesh = obj_tira.data
        vertices = mesh.vertices
        
        # Diccionario para agrupar vértices por posición aproximada
        nodos = {}
        
        #Esta vaina va dar problemas con ciertas longitudes pequeñas, pero bueno
        #En el futuro se resolvera.
        #la tolerancia creo que va a ser el depth*2+0.005
        #Este 0.005 seria como otra tolerancia para alcanzar algunos nodos perdidos.
        nu_tolerancia=(self.nu_grosor*2)+0.005
        
        for vert in vertices:
            #print("tuplas:",tuple(vert.co),vert.co,vert.index)
            pos = tuple(vert.co)
            encontrado = False

            # Buscar si ya existe un nodo cercano
            for nodo_central in nodos:
                #print('Distancia entre nodos:',(mathutils.Vector(pos) - mathutils.Vector(nodo_central)).length)
                if (mathutils.Vector(pos) - mathutils.Vector(nodo_central)).length <= nu_tolerancia:
                    nodos[nodo_central].append(vert.index)
                    encontrado = True
                    break

            # Si no se encontró un nodo cercano, crear uno nuevo
            if not encontrado:
                nodos[pos] = [vert.index]
        
        #pprint(nodos)
        #Obtener nombre core para los grupos
        matcheo=re.match(r"^(.*)\.(\d+)$", _objeto['tx_objeto_name'])
                
        if matcheo:
            prefijo, sufijo = matcheo.groups()
            tx_nombre_vertex_core=f"{prefijo}{int(sufijo)}"
        else:
            tx_nombre_vertex_core=_objeto['tx_objeto_name']
        
        # crear grupo para el shape
        grupo_shape=obj_tira.vertex_groups.new(name=tx_nombre_vertex_core+'_shape')
        _objeto['tx_vgshape']=grupo_shape.name
        
        # Crear vertex groups en el objeto para cada nodo
        #print('numero de nodos:', len(nodos.items()))
        for i, (nodo, vert_indices) in enumerate(nodos.items()):
            
            
            if i==0:
                grupo_shape.add(vert_indices, weight=1.0, type='ADD')
            else:
                tx_nombre_vertex=tx_nombre_vertex_core+'_V'+str(i)
                
                group = obj_tira.vertex_groups.new(name=tx_nombre_vertex)
                group.add(vert_indices, weight=1.0, type='ADD')
                grupo_shape.add(vert_indices, weight=0.2, type='ADD')
                #Vicular el grupo de vertices a los huesos
                #Es menos 1 porque estos nodos van a hacer uno mas que la cantidad de huesos.
                #Y el primer nodo no tiene huesos asignado, es el shape de la fisica de ropa.
                _objeto['lista_huesos'][i-1]['tx_vg']=group.name
                
                
                
        
        #pprint(_objeto)
        # Volver al modo pose con el armature seleccionado
        bpy.ops.object.select_all(action='DESELECT')
        self.objeto.select_set(True)
        bpy.context.view_layer.objects.active = self.objeto
        
        
        bpy.ops.object.mode_set(mode='POSE')
            
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def set_modificadores(self)->None:
        """
            Aqui aplicare todos los modificadores y terminare todo.
            en teoria seria creo que dos bucles.
        """    
        
        #PASO 1 asignar los padre a los huesos fisico y
        bpy.ops.object.mode_set(mode='EDIT')
        armature_edit = bpy.context.object
        
        for item in self.lista_tiras:
            hueso_fisico=armature_edit.data.edit_bones.get(item['lista_huesos'][0]['tx_physic'])
            hueso_parent=armature_edit.data.edit_bones.get(item['lista_huesos'][0]['tx_parent'])
            hueso_fisico.parent=hueso_parent
            
        bpy.ops.object.mode_set(mode='POSE')
        
        #PASO 2 asignar modificadores y fisica a lo bestia.
        for item in self.lista_tiras:
            
            obj_tira = bpy.data.objects.get(item['tx_objeto_name'])
            
            #Asignaciones individuales por huesos
            for obj_hueso in item['lista_huesos']:
                
                hueso_fisico = self.objeto.pose.bones.get(obj_hueso['tx_physic'])
                hueso_fk = self.objeto.pose.bones.get(obj_hueso['tx_fk'])
                
                #borrar restricciones anterior, por si acaso.
                while hueso_fisico.constraints:
                    hueso_fisico.constraints.remove(hueso_fisico.constraints[0])
                    
                while hueso_fk.constraints:
                    hueso_fk.constraints.remove(hueso_fk.constraints[0])
                
                #SUB-1 vincular los huesos fisicos con los vertex group
                
                const_damped=hueso_fisico.constraints.new(type='DAMPED_TRACK')
                const_damped.target = obj_tira  # Asignar el objeto objetivo
                const_damped.subtarget=obj_hueso['tx_vg']
                const_damped.influence = 1.0
                
                #SUB-2 vincular los huesos fk con los fisicos
                
                const_copy_rotation=hueso_fk.constraints.new(type='COPY_ROTATION')
                const_copy_rotation.target = self.objeto  # Asignar el objeto objetivo
                const_copy_rotation.subtarget=obj_hueso['tx_physic']
                
                const_copy_rotation.mix_mode = 'BEFORE'
                const_copy_rotation.target_space = 'LOCAL'
                const_copy_rotation.owner_space = 'LOCAL'
                const_copy_rotation.influence = 1.0
                
            #SUB-3 vincular los objetos tiras con el objeto armature
            bpy.ops.object.mode_set(mode='OBJECT')
            
            obj_tira = bpy.data.objects.get(item['tx_objeto_name'])
            bpy.ops.object.select_all(action='DESELECT')
            obj_tira.select_set(True)
            
            child_of_constraint = obj_tira.constraints.new(type='CHILD_OF')
            # Asignar el target al constraint
            child_of_constraint.target = self.objeto
            child_of_constraint.subtarget = item['lista_huesos'][0]['tx_parent']
            bpy.context.view_layer.objects.active = obj_tira
            bpy.ops.constraint.childof_set_inverse(constraint=child_of_constraint.name, owner='OBJECT')
            
            #SUB-4 aplicar la fisica de ropa con el shape
            tx_name_cloth=item['tx_objeto_name']+'.cloth'
            cloth_modifier = obj_tira.modifiers.new(name=tx_name_cloth,type='CLOTH')
            cloth_modifier.settings.vertex_group_mass = item['tx_vgshape']
            # Activar colisiones en las configuraciones de Cloth
            
            cloth_modifier.collision_settings.use_collision = True
            cloth_modifier.collision_settings.use_self_collision = True
            
            
            
            # volver a modo pose
            
            bpy.ops.object.select_all(action='DESELECT')
            self.objeto.select_set(True)
            bpy.context.view_layer.objects.active = self.objeto
            bpy.ops.object.mode_set(mode='POSE')
            
            
            
        
        print("PASO 6 aplicar modificadores: Completado")    
        
        
    
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #****************************GENERADORES*********************************
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def generar_grupos(self):
        # Crear la colección principal "cuerda" (si no existe)
        if self.tx_bcoll_name not in self.esqueleto.collections:
            self.bcoll_main = self.esqueleto.collections.new(self.tx_bcoll_name)
        else:
            self.bcoll_main = self.esqueleto.collections[self.tx_bcoll_name]
        
        
        #print("Colleccion principal: ",self.bcoll_main.children)
        # Crear subcolecciones dentro de "cuerda"
        tx_name_fk=self.tx_bcoll_name+'_FK'
        tx_name_ph=self.tx_bcoll_name+'_physic'
        tx_name_pa=self.tx_bcoll_name+'_parent'
        
        lista_bcoll_name_temp = [tx_name_fk,tx_name_ph,tx_name_pa]
        #self.lista_bcoll_name 
        lista_name=[item.name for item in self.bcoll_main.children]   
        #lista_name2=[item.name for item in armature.collections]
        #print(lista_name2)
        
        for sub_name in lista_bcoll_name_temp:
            # Crear la subcolección si no existe
            if sub_name not in lista_name:
               self.esqueleto.collections.new(sub_name,parent=self.bcoll_main)
        
        for bcoll_child in self.bcoll_main.children:
            if '_FK' in bcoll_child.name:
                self.bcoll_FK=bcoll_child
                
            if '_physic' in bcoll_child.name:
                self.bcoll_physic=bcoll_child
                
            if '_parent' in bcoll_child.name:
                self.bcoll_parent=bcoll_child
        
        #Es importante el orden asi que no cambien el orden o dara problemas.
        #0 -> fk 1->fisica 2->parent
        self.lista_bcoll_name=[self.bcoll_FK.name,self.bcoll_physic.name,self.bcoll_parent.name]
                    
        #print(self.bcoll_FK,self.bcoll_physic,self.bcoll_parent)
        print("PASO 2 generar grupos de huesos: completado.") 
        
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def generar_huesos_fisica(self)->None:
        """
            Esto generara los huesos que compondran el bone collection de physic;
            estos juesos seran los que hagan los movimientos fisicos.
            
            Estos basicamente seguiran los vertices de la malla fisica y pasaran estos
            datos de manera indirecta a los huesos principales (FK), para que estos
            puedan moverse de forma manual en caso de ser requerido.
            
        """
        # PASO 0 borrar huesos de fisica viejos.
        if len(self.bcoll_physic.bones)>0:
            lista_bcoll_physic_name=[bone.name for bone in self.bcoll_physic.bones]
            bpy.ops.object.mode_set(mode='EDIT')
            edit_bones = self.esqueleto.edit_bones
            edit_bcoll_delete=[edit_bones[bone_name] for bone_name in lista_bcoll_physic_name if bone_name in edit_bones]
            for bone in edit_bcoll_delete:
                edit_bones.remove(bone)
            bpy.ops.object.mode_set(mode='POSE')
        
        # PASO 1 preparar huesos, ya que las collecciones no funcionan en modo edicion.
        
        lista_bcoll_FK_name=[bone.name for bone in self.bcoll_FK.bones]
        lista_bcoll_physic_name=[]
        
        
        # PASO 2 Cambiar a modo edición
        bpy.ops.object.mode_set(mode='EDIT')
        print("uno")
        
        edit_bones = self.esqueleto.edit_bones
        edit_bcoll_FK=[edit_bones[bone_name] for bone_name in lista_bcoll_FK_name if bone_name in edit_bones]
        
        
        
        
        #print("tres dos")
        bone_map = {}  # {original_name: new_bone}
        
        
        
        #PASO 3 duplicar en seco
        for item in edit_bcoll_FK:
            #print("tres tres")
            # Crear un nuevo hueso con un nombre basado en el original
            tx_new_name=item.name.replace('_FK','_physic')
            new_bone = edit_bones.new(tx_new_name)
            new_bone.head = item.head
            new_bone.tail = item.tail
            new_bone.roll = item.roll
            new_bone.use_connect = item.use_connect
            
            lista_bcoll_physic_name.append(new_bone.name)
            # Registrar el duplicado en el diccionario
            bone_map[item.name] = new_bone 
            
            # Aqui repito el nombre para no tener que hacer maraña mas tarde para tenerlo.
            self.obj_vinculos_bones[item.name]={
                'tx_fk':item.name,
                'tx_physic':new_bone.name
            }
             
        
        #print("cuatro")    
        
        #PASO 2 ajustar padres e hijos
        for original_name, new_bone in bone_map.items():
            original_bone = edit_bones[original_name]
            if original_bone.parent:  # Si el hueso original tiene un padre
                parent_name = original_bone.parent.name
                if parent_name in bone_map:  # Verificar si el padre también fue duplicado
                    new_bone.parent = bone_map[parent_name]
        
        #print("cinco")  
        #PASO 3 Asignarlos al grupo fisico
        bpy.ops.object.mode_set(mode='POSE')
        pose_bones=self.objeto.pose.bones
        huesos_encontrados = [pose_bones[nombre] for nombre in lista_bcoll_physic_name if nombre in pose_bones]
        for item in huesos_encontrados:
            self.bcoll_physic.assign(item)
        
        self.bcoll_physic.is_visible=False 
        self.remove_collections(self.bcoll_physic.bones,self.lista_bcoll_name[1])
    
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def generar_huesos_parent(self)->None:
        """
            Esto generara los huesos que compondran el bone collection de parent
            estos juesos serviran de soporte a los huesos fisicos y en un futuro 
            a los huesos tracking.
            
            Estos huesos son muy individuales ya que solo se requiere el origen,
            es decir estos representa solo el comienzo de las tiras
        """
        # PASO 0 borrar huesos de parent viejos.
        if len(self.bcoll_parent.bones)>0:
            lista_bcoll_parent_name=[bone.name for bone in self.bcoll_parent.bones]
            bpy.ops.object.mode_set(mode='EDIT')
            edit_bones = self.esqueleto.edit_bones
            edit_bcoll_delete=[edit_bones[bone_name] for bone_name in lista_bcoll_parent_name if bone_name in edit_bones]
            for bone in edit_bcoll_delete:
                edit_bones.remove(bone)
            bpy.ops.object.mode_set(mode='POSE')
        
        # PASO 1 preparar huesos, ya que las collecciones no funcionan en modo edicion.
        #--AQUI SOLO AGARRO LOS HUESOS DE ORIGEN.
        lista_bcoll_FK_all=[bone for bone in self.bcoll_FK.bones]
        lista_bcoll_FK_name=[bone.name for bone in self.bcoll_FK.bones if not bone.parent or bone.parent not in lista_bcoll_FK_all]
        #print(lista_bcoll_FK_name)
        lista_bcoll_parent_name=[]
        
        
        # PASO 2 Cambiar a modo edición
        bpy.ops.object.mode_set(mode='EDIT')
        #print("uno")
        
        edit_bones = self.esqueleto.edit_bones
        edit_bcoll_FK=[edit_bones[bone_name] for bone_name in lista_bcoll_FK_name if bone_name in edit_bones]
      
        
        
        
        #print("tres dos")
        bone_map = {}  # {original_name: new_bone}
        lista_final_parent=[]
        
        
        #PASO 3 duplicar en seco
        for item in edit_bcoll_FK:
            #print("tres tres")
            # Crear un nuevo hueso con un nombre basado en el original
            tx_new_name=item.name.replace('_FK','_parent')
            new_bone = edit_bones.new(tx_new_name)
            new_bone.head = item.head
            new_bone.tail = item.tail
            new_bone.roll = item.roll
            new_bone.use_connect = item.use_connect
            new_bone.parent=edit_bones[self.tx_core_bone_name]
            
            #escalar al -50%
            nu_scale_factor=0.5
            
            new_bone.tail = new_bone.head  + (new_bone.tail - new_bone.head) * nu_scale_factor
            
            
            lista_bcoll_parent_name.append(new_bone.name)
            
            self.obj_vinculos_bones[item.name]['tx_parent']=new_bone.name
            #.append(new_bone.name)
            # Registrar el duplicado en el diccionario
            #bone_map[item.name] = new_bone  
        
        #print("cuatro")    
         
        #PASO 3 Asignarlos al grupo parent
        bpy.ops.object.mode_set(mode='POSE')
        pose_bones=self.objeto.pose.bones
        huesos_encontrados = [pose_bones[nombre] for nombre in lista_bcoll_parent_name if nombre in pose_bones]
        for item in huesos_encontrados:
            self.bcoll_parent.assign(item)
        
        self.bcoll_parent.is_visible=False 
        self.remove_collections(self.bcoll_parent.bones,self.lista_bcoll_name[2])
    
    
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def make_colleccion_fisica(self)->None:
        #PASO 1 BORRAR EXISTENTE
        self.tx_collecion_fisica=self.tx_bcoll_name+'_Physic'
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if self.tx_collecion_fisica in bpy.data.collections:
            coleccion = bpy.data.collections[self.tx_collecion_fisica]
            # Eliminar todos los objetos dentro de la colección
            for obj in list(coleccion.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
        
            # Eliminar la colección
            bpy.data.collections.remove(coleccion)
        
        #PASO 2 CREAR COLLECCION
        lacolleccion=bpy.data.collections.new(self.tx_collecion_fisica)
        bpy.context.scene.collection.children.link(lacolleccion)
        bpy.ops.object.mode_set(mode='POSE')
        
        
        print('PASO 5.1 generar colleccion: completado')
    
    
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def generar_tiras(self)->None:
        """
            Esto generara y llenara el arreglo de lista_tiras
        """
        lista_bcoll_FK_all=[bone for bone in self.bcoll_FK.bones]
        lista_bcoll_FK_name=[bone.name for bone in self.bcoll_FK.bones if not bone.parent or bone.parent not in lista_bcoll_FK_all]
        self.lista_tiras=[]
        for tx_name in lista_bcoll_FK_name:
            
            #Esto formara una matriz representando la cadena y los vinculos entre los tipos 
            #de huesos
            cadena=self.get_cadena(tx_name)
            lista_vinculos=[]
            for tx_hueso in cadena:
                lista_vinculos.append(self.obj_vinculos_bones[tx_hueso])
            
            #El origen sera el hueso de origen de la tira.
            objecto={
                "tx_origen":tx_name,
                "lista_huesos":lista_vinculos
            }
            
            self.lista_tiras.append(objecto)
            
        #print(self.obj_vinculos_bones)
        #print(self.lista_tiras)
        print("PARTE 4 generar tiras: completado")
        
        
        
        
    
    
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def generar_mallas_fisicas(self):
        """
            Esto generara el conjunto de mallas fisicas.
        """
        bpy.ops.object.mode_set(mode='OBJECT')
        #PASO 1 generar puntos
        for i,tira in enumerate(self.lista_tiras):
            tx_name=self.tx_bcoll_name[0].upper()+'P.00'+str(i+1)
            self.generar_malla(tira,tx_name)
            
        bpy.ops.object.mode_set(mode='POSE')
        print('PASO 5.2 generar mallas fisicas: completado')
        
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    def generar_malla(self,_obj_tira:object,_tx_name:str)->None:
        """
            Esto generara una malla individual que representa la tira fisica.
        """
        # Crear una nueva malla y objeto
        mesh = bpy.data.meshes.new(_tx_name)
        obj = bpy.data.objects.new(_tx_name, mesh)
        bpy.context.collection.objects.link(obj)
        armature=self.objeto.data
        matrix_world=self.objeto.matrix_world
        
        # Lista para almacenar vértices y aristas
        vertices = []
        edges = []
        
        # Recorrer la cadena de huesos y generar vértices y aristas
        for i, huesos in enumerate(_obj_tira['lista_huesos']):
            
            #Este deberia ser el hueso correspondiente al FK
            #Debe ser asi por conveniencia y porque el FK es el original y este es el que da
            #forma.
            bone = armature.bones.get(huesos['tx_fk'])
            
            if not bone:
                #print(f"Hueso '{huesos['tx_fk']}' no encontrado.")
                continue
            
            # Añadir vértices para head y tail del hueso
            head = matrix_world @ bone.head_local
            tail = matrix_world @ bone.tail_local
            vertices.append(head)
            vertices.append(tail)
            
            # Añadir aristas entre los puntos
            if i > 0:  # Conectar con el último tail
                edges.append((len(vertices) - 3, len(vertices) - 2))
            edges.append((len(vertices) - 2, len(vertices) - 1))
        
        # Crear la malla
        mesh.from_pydata(vertices, edges, [])
        mesh.update()
        
        
        
        # Eliminar el objeto de su colección actual
        for col in obj.users_collection:
            col.objects.unlink(obj)
            
        
            
        # Asignar a la colleccion correspondiente
        coleccion=bpy.data.collections[self.tx_collecion_fisica]
        coleccion.objects.link(obj)
        
        _obj_tira['tx_objeto_name']=obj.name
        
        
        
        
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #***********************FUNCIONES DELETE****************************
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------            
    def remove_collections(self,_lista_huesos,_tx_name):
        for hueso in _lista_huesos:
            for bcoll in hueso.collections:
                if bcoll.name !=_tx_name:
                    bcoll.unassign(hueso)
                
    
    
    
    def delete_bones(self,_lista):
        """
            Esto borrara los huesos pertenecientes a una collecion de huesos
        """
        #print("huesos a borrar:",_lista )
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = self.esqueleto.edit_bones
        edit_bcoll_delete=[edit_bones[bone_name] for bone_name in _lista if bone_name in edit_bones]
        for bone in edit_bcoll_delete:
            edit_bones.remove(bone)
        
        bpy.ops.object.mode_set(mode='POSE')
            
    def delete_all_before(self):
        """
            Esto borrara todas las estruccturas hechas en caso
            de cambiar el nombre principal.
            
            si la logica no me falla esto solo funcionara mientras el
            addon este activo, ya que si se limpia el cache o se carga
            de nuevo esto, creo que esto dejara de ser efectivo ya que 
            se borrara el historial.

            Actualizacion 09/12/2024
            Eso de arriva no funciono, ya que cuando se busca tener varias estructuras a la vez
            este metodo elimina todo dejando solo uno.

            ahora voy a provar hacer esta eliminacion segun los huesos seleccionados.
            ok, voy a basar esto en el grupo de hueso.

            voy a chequear no por lista before si no por grupo, asi sera mas exacto creo 
            y no tendre que preocuparme de cache o de importacion.

        """

        bpy.ops.object.mode_set(mode='POSE')
        if len(self.lista_before_bcoll)<=0:
            return



        #PASO 1 CHEQUEAR QUE GRUPO DE HUESOS PERTENECEN LOS HUESOS SELECCIONADOS.
        lista_bcoll_select=[]
        print("Collecciones:")
        for bone in self.bone_pose_selected:
            #print(bone.name)
            for cole in bone.bone.collections:
                #print(cole.name)
                if cole.name not in lista_bcoll_select and '_FK' in cole.name:
                    #Aqui agrego el nombre del posible padre.
                    lista_bcoll_select.append(cole.name[:-3])
                    print(cole.name,lista_bcoll_select)
        print("*********")
        pprint(lista_bcoll_select)
        #for tx_name in self.lista_before_bcoll:
            #BUSCAR GRUPOS PRINCIPAL
            #if tx_name in self.esqueleto.collections:
                #BUSCAR POR SUBGRUPO FK
                #for bone_col in self.esqueleto.collections.get(tx_name).children:
                    #for huesos_col in bone_col.bones:


        #PASO 2 BORRAR SEGUN LAS COLLECCIONES ACTUALES DE LOS HUESOS SELECCIONADOS
        #Con esto puedo borrar solo los grupos a los que pertenecen los huesos seleccionados de manera directa
        #sin tener que usar un historico temporal


        #for tx_name in self.lista_before_bcoll: #este es el parametro viejo, lo tendre aqui por si acaso


        for tx_name in lista_bcoll_select:
            #PASO 1 BORRAR LOS OBJETOS.
            collecion_fisica=tx_name+'_Physic'
            bpy.ops.object.mode_set(mode='OBJECT')
        
            if collecion_fisica in bpy.data.collections:
                coleccion = bpy.data.collections[collecion_fisica]
                # Eliminar todos los objetos dentro de la colección
                for obj in list(coleccion.objects):
                    bpy.data.objects.remove(obj, do_unlink=True)
        
                # Eliminar la colección
                bpy.data.collections.remove(coleccion)
            
            
            
            #-------------------------------------------------
            #-------------------------------------------------
            #-------------------------------------------------
            
            #PASO 2 BORRAR COLLECCIONES DE HUESOS Y SUS HUESOS
            bpy.ops.object.mode_set(mode='POSE')
            bone_collection = self.esqueleto.collections.get(tx_name)
            
            #Aqui me aseguro a resguardar lo existente cuando el nombre concuerda
            if tx_name!=self.tx_bcoll_name and bone_collection is not None:
                #print("nombres: ",tx_name,self.tx_bcoll_name)
                #print("main bone colleccion")
                tx_main_name=bone_collection.name
                lista_child_name=[]
                #BORRAR MAIN COLLECTION BONES
                lista_main=[bone.name for bone in bone_collection.bones]
                self.delete_bones(lista_main)
                
                for childbcoll in bone_collection.children:
                    lista_child_name.append(childbcoll.name)
                    if '_FK' in childbcoll.name:
                        #PESERVAR LOS HUESOS ORIGINALES
                        
                        #borrar restricciones
                        
                        
                        for bone_child in childbcoll.bones:
                            
                            elbone=self.objeto.pose.bones.get(bone_child.name)
                            while elbone.constraints:
                                elbone.constraints.remove(elbone.constraints[0])
                        
                        self.remove_collections(childbcoll.bones,childbcoll.name) 
                    else:
                        #BORRAR COLLECTION BONES HIJOS
                        lista_child=[bone.name for bone in childbcoll.bones]
                        self.delete_bones(lista_child)
                        
                
                
                #BORRAR LAS COLLECCIONES
                try:
                    delete_bcoll_main=self.esqueleto.collections.get(tx_main_name)
                    #print('lista_delete',lista_child_name)
                    for delete_bcoll in list(delete_bcoll_main.children):
                        #print('hijo delete',delete_bcoll)
                        self.esqueleto.collections.remove(delete_bcoll)
                
                
                    self.esqueleto.collections.remove(delete_bcoll_main)
                except Exception as e:
                    pass
                    #print(e)
            
                
        
        self.lista_before_bcoll=[]
        bpy.ops.object.mode_set(mode='POSE')

        
        


    