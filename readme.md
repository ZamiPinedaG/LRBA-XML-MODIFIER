# Control-M XML Modifier

Este programa está diseñado para modificar archivos XML de Control-M y adaptarlos a diferentes entornos. Realiza cambios específicos en las etiquetas `VALUE`, `JOBNAME`, `NODEID`, `CMDLINE`, entre otras, según el entorno (calidad o producción), y aplica una serie de validaciones y reglas configurables.

## 1. Recomendaciones de Uso

### 1.1 Estructura del Script

Este script está dividido en funciones clave que manejan aspectos específicos del archivo XML, como `JOBNAME`, `NODEID`, `CMDLINE`, y `DOMAIL`. Cada una de estas funciones tiene una tarea específica, facilitando la modificación del XML según las configuraciones.

### 1.2 Configuración del Logger

Es esencial configurar el logger adecuadamente para monitorear las operaciones del script. El logger permite registrar errores, advertencias y la evolución del proceso. 
Recomendamos ajustar el nivel del logger (`INFO`, `DEBUG`) dependiendo de si el script se ejecuta en un entorno de pruebas o producción.

### 1.3 Manejo de Configuraciones por Ambiente

Se utilizan configuraciones diferentes para ambientes de calidad y producción. Asegúrate de actualizar los valores en `CONFIGURACION_CALIDAD` y `CONFIGURACION_PRODUCCION` en el archivo `config.py` según los cambios en tus entornos. 

### 1.4 Prefijos Grandes y Pequeños

Los prefijos `PATRON_PREFIJOS_GRANDES` y `PATRON_PREFIJOS_PEQUENOS` definen los valores a cambiar en el `JOBNAME`. La función `modificar_jobname` verifica y actualiza estos prefijos según el ambiente. Asegúrate de actualizar las listas `PREFIJOS_PEQUENOS` y `PREFIJOS_GRANDES` en `config.py` para reflejar cualquier cambio.

### 1.5 Contadores

El script utiliza contadores para llevar un registro de cambios en diferentes elementos (e.g., `CONTADOR_CMDLINE`, `CONTADOR_NODEID`). Esto permite una verificación fácil de cuántos elementos fueron modificados. Recomendamos revisar estos contadores después de cada ejecución para asegurarse de que se aplicaron todos los cambios esperados.

### 1.6 Modificación de Variables y Condiciones

Las funciones `modificar_cmdline`, `modificar_nodeid`, `modificar_variable`, y `modificar_condiciones` permiten modificar valores específicos en `VARIABLE` y condiciones como `INCOND` y `OUTCOND`. 
- **Recomendación:** Asegúrate de que las expresiones regulares en `constants.py` estén bien definidas para detectar correctamente los elementos a modificar.

### 1.7 Administración de Dependencias

Antes de ejecutar el script, confirma que las dependencias en `constants.py`, `config.py`, y `logger_setup.py` están correctamente configuradas. Los constantes y configuraciones cargadas en estos archivos son fundamentales para la ejecución correcta del script.

### 1.8 Verificación del XML Modificado

Es importante revisar el XML de salida para asegurar que los cambios aplicados sean correctos. Esto puede lograrse usando herramientas de validación de XML o cargando el archivo en el entorno de Control-M y verificando que las modificaciones sean aceptadas por el sistema.

## 2. Ejecución del Script

Para ejecutar el script, simplemente usa el siguiente comando desde la línea de comandos:

```bash
py lrba.py
# El nombre del archivo, con la extensión .xml
- Ingrese el nombre del archivo XML (con extensión): archivo.xml
# Si desea generar automaticamente la etiqueta QUANTITATIVE, esto puede conllevar a modificar el formato.
- ¿Desea modificar las etiquetas QUANTITATIVE? (s/n)
# Agregara automaticamente los correos en los distintos ambientes, si desea puede modificar el destinatario en `config.py` tener presente que sobreescribira si selecciona afirmativamente.
- ¿Desea modificar las etiquetas DOMAIL? (s/n)
# En los nombres de archivos al usar la variable ##ODATE. desaparecera el '.', por buenas prácticas se colocan dos para evitar problemas
- ¿Desea modificar las variables %%ODATE para agregar '..' de ser necesario? (s/n)
# Modificara los jobs tomando en cuenta la etiqueta JOBNAME y obtendra los últimos dos caracteres
- ¿Desea modificar solo jobs en especifico? (s/n)
- Ingrese los últimos dos caracteres de los jobs a modificar, separados por comas (ej: 01,02,03)
- Ingrese el ambiente (calidad/produccion)
```

## 2.1 Ejecución del Script - Ejemplo caso de uso

Verificar que archivo xml esta dentro del proyecto antes de iniciar.

```bash
py lrba.py
- Ingrese el nombre del archivo XML (con extensión): CR-COCTSUEVEC-T03.xml
- ¿Desea modificar las etiquetas QUANTITATIVE? (s/n):
- ¿Desea modificar las etiquetas DOMAIL? (s/n):
- ¿Desea modificar las variables %%ODATE para agregar '..' de ser necesario? (s/n):
- ¿Desea modificar solo jobs en especifico? (s/n): s
- Ingrese los últimos dos caracteres de los jobs a modificar, separados por comas (ej: 01,02,03): 22,23
- Ingrese el ambiente (calidad/produccion): produccion
```

## 3. Buenas Prácticas

- Backups del XML Original: Antes de realizar cambios en un archivo XML, realiza una copia de seguridad. Esto te permitirá restaurar el archivo en caso de que ocurra algún problema.
- Validación Regular de Configuraciones: Dado que las configuraciones de ambientes pueden cambiar con el tiempo, es buena práctica revisar y validar los valores en config.py periódicamente.
- Pruebas en Ambiente de Desarrollo: Ejecuta el script en un ambiente de pruebas antes de aplicarlo en producción para verificar que todos los cambios funcionen correctamente.

## 4. Estructura del Proyecto

- `lrba.py`: Archivo principal donde se ejecuta el programa y se aplican todas las modificaciones al archivo XML.
- `config.py`: Archivo de configuración donde se definen:
  - **Prefijos** para las unidades aplicativas, que se utilizan en las modificaciones del programa con el indicativo de Colombia.
  - **Variables de entorno** para los diferentes ambientes (`calidad` y `producción`).
- `constants.py`: Archivo que contiene las constantes utilizadas en el programa, como los nombres de las etiquetas XML, los atributos específicos y cualquier otra constante requerida.
- `logger_setup.py`: Este archivo define la configuración para el sistema de logging del programa, centralizando la forma en que los mensajes de log son capturados, formateados y almacenados. 
- 
### 4.1 Configuración de Formato Logger

Cada mensaje de log incluye:
- Fecha y Hora (asctime): Marca el momento en que ocurre el evento.
- Nombre del Logger (name): Identifica el origen del log dentro de la aplicación.
- Nivel del Log (levelname): Indica la severidad del mensaje (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- Mensaje (message): El mensaje descriptivo del evento.

### 4.2 Detalles de Almacenamiento

Directorio de Logs:
Si no se especifica otro, los logs se guardan en una carpeta llamada "log" en el directorio de ejecución del script.
Si la carpeta "log" no existe, el script la crea automáticamente.

#### 4.2.1 Archivo de Log:

La información se guarda en un archivo llamado "script.log" por defecto, o en el nombre especificado en el parámetro log_file de la función setup_logger.
Cada entrada de log incluye una marca de tiempo, el nombre del logger, el nivel de severidad y el mensaje.

##### 4.2.1.1 Rotación de Archivos:

El archivo de log tiene una capacidad máxima de 100 MB.
Al superar los 100 MB, el archivo de log se rota, guardando hasta 5 versiones antiguas del archivo. La rotación garantiza que los logs más antiguos se eliminen cuando se supera el límite, manteniendo solo las 5 versiones más recientes.

##### 4.2.1.2 Formato de Log:

Cada línea en el archivo de log tiene el formato:

```bash 
YYYY-MM-DD HH:MM:SS,ms - logger_name - SEVERITY_LEVEL - message
```

## 5. Configuración

### `config.py`

Este archivo define los **prefijos** y **variables por entorno**. Aquí es donde puedes personalizar los valores que el programa usará según el ambiente en el que se esté ejecutando (por ejemplo, prefijos diferentes para `calidad` o `producción`). 
#   C o n t r o l - M - X M L - M o d i f i e r  
 #   L R B A - X M L - M O D I F I E R  
 