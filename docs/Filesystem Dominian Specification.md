Filesystem Domain Specification

MEKA Core SDK

Estado: Borrador 1.0
Dominio: Filesystem
Prioridad: Alta

1. Objetivo

El dominio Filesystem es el responsable de todas las operaciones sobre el sistema de archivos.

Su función es proporcionar una API unificada, estable e independiente de la plataforma para manipular archivos y directorios.

El dominio abstrae completamente la implementación utilizada para realizar cada operación.

El consumidor del SDK nunca interactúa directamente con bibliotecas externas ni con herramientas del sistema operativo.

2. Responsabilidades

El dominio es responsable de:

lectura de archivos
escritura de archivos
escritura parcial
lectura parcial
lectura por streaming
administración de archivos
administración de directorios
obtención de metadatos
exploración del filesystem
búsqueda de archivos
búsqueda de texto
observación de cambios del filesystem
resolución de rutas
3. No es responsabilidad del dominio

Filesystem no interpreta el contenido de los archivos.

Por lo tanto quedan fuera del dominio:

análisis sintáctico
análisis semántico
Tree-sitter
LSP
CodeQL
AST
refactorizaciones
formateo de código
reemplazo de funciones
renombrado de símbolos
edición estructural

Estas capacidades pertenecerán al futuro dominio Code Analysis.

4. Principios arquitectónicos
API estable

La API pública nunca depende de una biblioteca determinada.

Ejemplo:

filesystem.search_text(...)

Nunca:

ripgrep.search(...)
Backends internos

Las implementaciones son un detalle interno.

El dominio puede cambiar completamente el backend sin modificar la API pública.

Independencia del lenguaje

Filesystem trabaja sobre archivos.

No importa si contienen:

Python
Java
C#
Markdown
JSON
XML
imágenes
binarios
Operaciones composables

Cada operación debe resolver un único problema.

Las operaciones pueden combinarse para implementar funcionalidades de mayor nivel.

Soporte para archivos grandes

El dominio debe permitir trabajar con archivos de cualquier tamaño.

La implementación decidirá cuándo utilizar:

lectura completa
lectura parcial
streaming
otras estrategias optimizadas

El consumidor no necesita conocer dicha decisión.

Resolución centralizada de rutas

Todas las operaciones reciben rutas.

Antes de acceder al filesystem todas deberán utilizar el resolvedor del dominio.

No se permitirá que cada operación implemente su propia lógica de resolución.

5. Arquitectura
filesystem/

    api.py

    operations/

        # Lectura

        read.py
        read_range.py
        stream.py
        head.py
        tail.py

        # Escritura

        write.py
        append.py
        write_range.py
        truncate.py

        # Administración

        delete.py
        move.py
        copy.py
        mkdir.py

        # Información

        exists.py
        stat.py

        # Exploración

        list.py
        walk.py
        glob.py
        grep.py

        # Observación

        watch.py

    backends/

        ripgrep.py
        watchdog.py

    path.py

    models.py

    errors.py
6. API pública

La API pública inicial estará compuesta por las siguientes capacidades.

Lectura
read()

read_range()

stream()

head()

tail()
Escritura
write()

append()

write_range()

truncate()
Administración
delete()

copy()

move()

mkdir()
Información
exists()

stat()
Exploración
list()

walk()

glob()

grep()
Observación
watch()
7. Resolución de rutas

El dominio contará con un componente dedicado denominado:

path.py

Será el único responsable de:

normalización
expansión
resolución de rutas relativas
resolución de rutas absolutas
validación
canonicalización

Toda operación deberá utilizar este componente antes de acceder al sistema de archivos.

8. Backends

Los backends son internos al dominio.

El consumidor nunca interactúa con ellos directamente.

Backend de búsqueda

Capacidad:

grep()

Backend inicial:

ripgrep
Backend de observación

Capacidad:

watch()

Backend inicial:

watchdog

La implementación podrá cambiar en cualquier momento sin afectar la API pública.

9. Límites del dominio
Operación	Filesystem	Code Analysis
Leer archivo	✓	
Escribir archivo	✓	
Leer parcialmente	✓	
Escribir parcialmente	✓	
Streaming	✓	
Append	✓	
Truncate	✓	
Copiar	✓	
Mover	✓	
Eliminar	✓	
Crear directorios	✓	
Obtener metadatos	✓	
Listar directorios	✓	
Recorrer directorios	✓	
Buscar archivos	✓	
Buscar texto	✓	
Watch filesystem	✓	
Reemplazar función		✓
Renombrar símbolo		✓
Agregar imports		✓
Modificar AST		✓
Tree-sitter		✓
LSP		✓
CodeQL		✓
10. Auditorías utilizadas

Las decisiones arquitectónicas de este dominio se basan en las siguientes auditorías técnicas.

Auditoría	Resultado
Open Terminal	Identificación de algoritmos reutilizables
utils/fs.py	Base para operaciones de filesystem
main.py	Separación entre API HTTP y lógica reutilizable
runner.py	Determinado que no pertenece al dominio Filesystem
watchdog	Adoptado como backend para watch()
ripgrep	Adoptado como backend para grep()
11. Trabajo futuro

Las siguientes capacidades quedan fuera del alcance de este dominio y serán tratadas en futuros dominios del SDK:

Code Analysis
Tree-sitter
Language Server Protocol (LSP)
CodeQL
edición semántica
navegación por símbolos
refactorizaciones
análisis del AST
formateadores de código
12. Decisiones arquitectónicas
La API pública representa capacidades, no implementaciones.
Los backends son completamente internos al dominio.
Cada operación tendrá un único archivo y una única responsabilidad.
El dominio será independiente del lenguaje y del tipo de archivo.
La resolución de rutas estará centralizada en path.py.
El dominio deberá soportar archivos grandes mediante operaciones específicas (read_range, stream, write_range, append, truncate), sin obligar a cargar el archivo completo en memoria.
La edición inteligente del contenido queda explícitamente fuera del dominio Filesystem y será responsabilidad del futuro dominio Code Analysis.
