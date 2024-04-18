 generate_cylinder(flame_video_name)
	lee nombre_video
	busca si el vídeo tiene los archivos generados por generate_armature
	si no:
		raiseError(...)
	busca si existe el archivo con los parámetros del cilindro
	si no:
		raiseError(...)
	
	comprueba si el nombre del armature correspondiente a flame_video_name existe
	si existe:
		armature = el armature de la escena
		bound_name = el nombre del cilindro
		si el cilindro no existe en la escena:
			pasar a modo object
            deselect all
            offset = coordenadas globales de la base del armature
            llama = el objeto de la llama

            altura cilindro = altura llama + 0.01 (para q no se produzca el bug)
            radio cilindro = radio de la llama + un poquito más para que quepa la llama en el cilindro

            añadir cilindro con altura y radio mencionados
            le cambiamos el nombre por bound_name

            cilindro = el cilindro que acabamos de crear (el active_object)

            loc = location de la llama
            cilindro.location = loc

            deselect all
            objeto activo = cilindro
            pasar a modo edit
            update escena
            abrimos fichero cfg (el que tiene los parámetros del cilindro en cada frame):
                lines = lineas del archivo
            lines contiene todas las lineas del archivo, cada línea a partir de la segunda representa un frame, y cada línea consta de 12 parejas, las distancias izquierda y derecha de cada anillo,
            es decir tiene la siguiente forma:
            linea0_izq linea0_der linea1_izq linea1_der … … linea11_izq linea11_der
            la primera linea, en cambio, son los puntos de la llama donde se hacen estas líneas. Es decir, las coordenadas de la
            llama donde el cilindro tendrá los anillos. 
            guardamos estos puntos en division_points
            for i in division_points:
                pasamos i a coordenadas locales del cilindro. Esto servirá para poder hacer los loop cuts

            usamos una función para encontrar unos parámetros de otra función que tenemos que usar para que funcione el loopcut and slide.
            es un lío, lo encontré en un foro y funcionó.
            verts = [], una lista vacía que nos permitirá guardar los vertices, lo explico más abajo.
            for idx, x in enumerate(local_division_points):
                EXPLICACIÓN: la función loopcut and slide funciona de tal manera que el lugar en el que cortas se calcula con un value [-1.0, 1.0],
                siendo 0.0 la zona inferior y 1.0 la zona superior. Una vez haces un corte, creas dos subdivisiones. Bien, pues luego estas dos
                subdivisiones tambien tienen su respectivo rango de [-1.0, 1.0], se explica mejor con la siguiente imagen:
                ![Alt text](https://i.imgur.com/YxnxjVa.jpeg "Loop Cut and Slide")
                Por lo tanto, he hecho una pequeña función en la que:
                1. cojo value = local_division_points[idx] (o mejor dicho, x)
                2. si idx > 0:
                    · a value le resto local_division_points[idx-1.], es decir, me quedo con la diferencia del punto anterior con el de ahora. Es decir, que esta es la distancia (en coordenadas locales) que tendré que recorrer desde el último loop cut hacia arriba para hacer el nuevo loop cut.
                    · ahora hago value = value / (1 - local_division_points[idx-1]). Esto lo hago para escalar de 0 a 1 esa distancia que tengo que recorrer. Es decir, paso de coordenadas locales de todo el cilindro a coordenadas locales de la subdivisión.
                3. hago value = - value + (1 - value). Esto es para escalar value de -1 a 1.
                ahora uso loopcut_slide, con valor = value y, ojo, edge_index = 2. Me di cuenta que, si escojo el segundo edge, siempre hará el loopcut hacia arriba, ya que cuando vas a hacer un loopcut tienes que escoger la mitad superior o inferior de la(s) arista(s) vertical(es) que vas a cortar. Por eso empezamos a hacer loopcuts desde más abajo, hasta el último, que es el de arriba.

                paso a modo objeto

                una vez hecho el loopcut, se quedan seleccionados los vertices y edges creados. La cosa es que la selección de loopcuts en blender es un problema que mucha gente tiene en la comunidad, la gente crea algoritmos complejos, sería muy difícil hacerlo nosotros encima teniendo 12. Lo más sencillo es, despues de crear cada loopcut, almacenar en un vector los edges y vertices seleccionados, es decir, los recientemente creados, así tenemos acceso rápido a ellos. Me acabo de dar cuenta, por cierto, que los edges son innecesarios guardarlos, ya que con los vertices tenemos suficiente.

                Dicho esto, el codigo sigue así:

                selected_verts = [recorro los vertices del cilindro y los guardo si están seleccionados, creo que no hay otra forma de guardar los vertices seleccionados]

                verts.append(selected_verts), una lista de listas es la mejor forma de guardar los vértices de cada cilindro. verts[0]
                son los vértices del primer cilindro, verts[1] del segundo...

                **De todas formas CREO que esto se puede mejorar, ya que los vértices creados nuevos CREO que siempre se guardan al final de la lista de vértices de la figura. Osea que no haría falta recorrer cada vez los vértices seleccionados etc.**
            end for

            pasamos a modo objeto
            deseleccionamos todos los edges y vertices del cilindro. Creo que esto se puede quitar, y simplemente usar un deselect all.
            pasamos a modo edit

            initial_vertex_locations = [las coordenadas de cada vértice del cilindro] esto se hace porque, al inicio de cada frame, tendremos que devolver los vertices a su posición inicial. Intenté hacerlo de otras formas, pero solo es posible así, debido al método de deformación que usamos para cada anillo.

            cilindro.select_set(True) no sé si es necesario, tengo q probar a quitarlo
            pasamos a modo objeto

            for frame in range(len(lines)-2): hacemos un range de lines - 2 porque el número de frames = número de líneas + 2, es una manera rápida de saber los frames de un vídeo procesado sin tener que apuntarlos en algún lado o pasarlos como variable
                width_frame = [], aquí guardaremos la amplada de cada loop cut (anillo) del frame actual, lo leeremos de lines
                set frame al frame actual
                dos variables para hacer los keyframe bien
                if frame > 0:
                    pasamos a modo objeto
                    aquí básicamente hacemos un zip de los vertices del cilindro e initial_vertex_locations, y, además de seleccionar el vértice, movemos cada vértice a su posición inicial. Lo único que se me ocurre para optimizar un poco esto, es no seleccionando los vértices que no modificamos, es decir los de los anillos superior e inferior. Esto serían 64 iteraciones menos (32 x 2). Además, creo que no es posible modificar el objeto solo para el frame actual. Es decir, que si estoy editando el frame n, en el frame n+1, si no cambio nada, seguirá como en el frame n.
                pasamos a modo edit
                deselect all, solo funciona en modo edit
                pasamos a modo object
                widths = cogemos las ampladas de la linea correspondiente al frame. hacemos frame + 1 ya que en el archivo las ampladas de los frames empiezan en la línea 2 (lines[1]). hacemos un split porque van separadas por espacios
                for i in range(0, len(widths),2):
                    básicamente en este for vamos de dos en dos en widths, y los guardamos como [izq,der] en width_frame. Este for es solo para hacer una lista más ordenada. Se puede quitar si lo necesitamos. También multiplicamos cada width por un valor llamado 'escala', esto era una idea que se me ocurrió que nos podía servir para escalar las ampladas, por si queriamos hacer una variable en el addon...
                end for

                width_frames es una lista de la siguiente forma:
                [[izq0,der0],[izq1,der1],...,[izq11,der11]], es decir cada elemento de la lista representa un anillo (loopcut), y tiene su amplada de izquierda y su amplada de derecha.

                for idx, x in enumerate(width_frames): 
                    nos guardamos w_left y w_right de x
                    verts_frame = guardamos los vertices correspondientes al anillo que usaremos.
                    verts_frame_left = los vertices de la izquierda, es decir los primeros 16
                    verts_frame_right = los de la derecha, los ultimos 16
                    for vert in verts_frame:
                        seleccionamos los verts
                    pasamos a modo edit
                    escondemos los vértices NO seleccionados. Esto lo hacemos para dejar solo a la vista el anillo que vamos a editar, de manera que podamos hacer escalados proporcionales sin editar otros anillos.
                    ![Alt text](https://i.imgur.com/33rSjVr.jpeg "Hide(unselected)")
                    Los escalados deben ser proporcionales para hacer la deformación que deseamos.

                    Ahora viene la chicha. Como bien sabemos, en la llama muchas veces encontramos casos en las que de un lado tiene más ancho que en el otro. En 2d es muy simple, pero pasarlo a 3d, como es un cilindro, requiere un poco más de técnica. A mí se me ocurrió hacer una deformación de manera que, visto en 2d, las anchuras de izquierda y derecha se respeten, pero que modifiquen la circunferencia del anillo y no quede una redonda perfecta. Esta deformación se hace de la siguiente forma:

                    1. Escalamos todo el anillo de manera que su radio = max(anch_izq,anch_der).
                    2. Si min(anch_izq,anch_der) = anch_izq, seleccionaremos los vértices de la mitad izquierda del anillo (verts_frame_left). Si no, verts_frame_right.
                    3. Ahora con los vértices seleccionados, tendremos que hacer un escalado proporcional cuyo radio de proporción sea JUSTO hasta llegar al vértice del otro extremo
                    ![Alt text](https://i.gyazo.com/de17cca24f8481e9e4db6e2ec96993c2.png "Radio de proporción")
                    de esta forma, moveremos los vértices de un solo lado, pero afectando a todo el anillo, sin mover el vertice del otro extremo para que este respete la anchura que le corresponde. Esto requiere un cálculo que me costó bastante saber, ya que necesitabamos, entre otras cosas, encontrar el median point (el centro del círculo de proporción).
                    También escalar todo para poder hacer el resize, etc.

                    Esto es para los dos primeros if (if w_left > w_right, y viceversa). En caso de que las distancias sean iguales, el anillo será una circunferencia normal y corriente y se hará un resize normal.

                    finalmente, seleccionamos todos los vértices para crear el keyframe. No sé si es necesario seleccionar los vertices, juraría que sí, pero es tan líoso que no recuerdo si se puede quitar.

                    Pasamos a modo edit y deseleccionamos todos los verts, hacemos el unhide (reveal), y pasamos a modo objeto.

                end for
            end for

            pasamos a modo objeto (creo que se puede borrar)
            set frame al 0
            seleccionamos el armature y el cilindro, y los bindeamos. Ahora el armature dará movimiento al cilindro.

            y estas últimas líneas sirven para crear el mesh deform en la llama y bindear esta con el cilindro, de manera que le da tanto movimiento como la deformación de amplada.



CONCLUSIONES: reconozco que al código le sobran varias cosas, algunas funciones que hacen cosas repetitivas, pero estaba tan liado haciendo el código que al final ni me daba cuenta de todo lo que se estaba acumulando. Exceptuando esto, quizás veo un par de cosas que optimizar, la deselección de vertices y edges con DESELECT ya debería ser suficiente, en cambio para seleccionar todos los vertices no se si hay otra forma, yo no he encontrado otra en foros. También, y como ya he dicho previamente, podría ser posible ahorrarme el guardar los vertices seleccionados, ya que sabemos exactamente cuantos vertices nuevos creamos, y si se añaden al final del vector de vértices, se pueden acceder a ellos fácilmente.