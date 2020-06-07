--------------------------------
| Funcionamiento y guía de uso |
--------------------------------

El fichero de main_all.c incluye todos los benchmarks de estudio, y los ejecuta secuencialmente uno detrás de otro,
repitiendo esto último un total de 10 veces. Por defecto, utiliza el STANDARD_DATASET del benchmark polybench, pero
es posible cambiarlo definiendo en el fichero polybench.h SMALL_DATASET o MINI_DATASET, para conjuntos de datos de 
entradas más pequeños.

Para ejecutarlo, es necesario enlazar todos los ficheros manualmente, y luego compilarlos generando el fichero ejecutable
con todas las dependencias bien distribuidas.