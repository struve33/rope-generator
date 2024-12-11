# Generador de cuerdas

Este add-on de blender consiste basicamente en generar unas estructuras hechas de huesos y mallas que van a simular tecnimente unas 'cuerdas'.

Estas 'cuertas' van a hacer de tal forma que por un lado tengan una fisica basica de ropa y por otra parte tu podras manualmente manipular su movimiento en la animación.


## Tabla de contenido

* [Introducción](#Introducción)
  * [Estructura](#Estructura)
  * [Utilidad](#Utilidad)
* [Tutorial](#Tutorial)
* [Declaración y Aclaración](#Declaración-y-Aclaración)
* [Futuro previsto](#Futuro-previsto)

## Introducción
### Estructura

Hablando de lo tecnico, este add-on forma 3 estructuras dos de huesos y una de malla, a la cual se le suma a la estructura base que se le va a aplicar el add-on, la cual sera los  huesos FK

1. Estructura huesos FK: son los huesos base de manipulacion directa/manual.

2. Estructura huesos Parent: Estan compuestos por el origen de los huesos FK, esto serviran como ancla y guia para los huesos fisicos.
 
3. Estructura huesos fisicos: son un clon de los huesos FK y estos seguiran de manera indirecta la malla con fisica.

4. Malla fisica: Esta malla tendra una forma parecido a una tira, por eso el nombre del add-on, ahora bien esta 'cuerda' tendra una fisica basica de ropa y estara anclara a los huesos parent. 

### Utilidad

La utilización de este add-on podria ser util para animar cuerdas, cabello, o faldas; Teniendo como ventaja la capacidad de tener control manual en ciertas areas, asi como la capacidad de poder intervenir manualmente en las estructuras generadas, para tener un mejor resultado de acuerdo a las necesidades.

## Tutorial
### Pasos a seguir.
#### PASO 1
Debes estar en modo pose.

#### PASO 2

Una vez en el modo pose, selecciona los huesos a los cuales quieres generer la estructura.

Es importante que en caso de ser varias estructuras de hueso esten todos  viculados a un mismo hueso raiz. Ejemplo varios mechones de pelos estaran vinculados a un hueso raiz que sera la cabeza. Si no va a dar error.

!["Select bones"](/images/tuto1.png?raw=true "Select Bones")

#### PASO 3
En la interfas grafica (ubicada en la pestaña 'Animation') tendras dos inputs.

1. **nombre:** Este le dara un nombre a la estructura que vas a generar; por defecto genera uno al azar.

2. **Grosor:** Esto sera el grosor de las mallas que formaran las 'cuerdas', esto afectara el movimiento asi que pendiente.

!["UI"](/images/tuto2.png?raw=true "UI")

#### PASO 4
Eso seria todo, solo resta presionar el boton de generar y ya todo estara listo.


!["Final1"](/images/tuto3.png?raw=true "Final1")
!["Final2"](/images/tuto4.png?raw=true "Final2")
### Pruebas ejecutadas y efectos esperados
1. No deberia haber cambios si ejecutas la instruccion varias veces sobre los mismos huesos seleccionados; ya que internamente borra todo y genera todo de nuevo.

2. Al ejecutarse por primera vez, cambiara los nombre de los huesos base de tal forma que agregara '_FK' al final del nombre.

3. Internamente genera algunas collecciones de huesos y mallas.

4. Puede generar varias estructuras diferentes en el misma armature.

5. Al aplicar esto sobre huesos con estructuras generadas, ocurrira que las viejas estructuras seran eliminadas, asi que ten cuidado.

## Declaración y Aclaración

Actualmente este proyecto es un prototipo y no cuenta con muchas pruebas de calidad, asi que se desea paciencia y comprensión sobre los posibles errores y mal funcionamiento.

## Futuro previsto

Si el proyecto avanza se prevee las siguientes adiciones:

 1. Agregar una estructura que sirva de guia.

 2. Nodos extras en la malla para aumentar la calidad de la fisica.

 3. una union entre las 'cuerdas' para brindar mayor consistencia a los movimientos.






