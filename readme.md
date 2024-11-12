# Control-M XML Modifier

Este programa está diseñado para modificar archivos XML de Control-M y adaptarlos a diferentes entornos. Realiza cambios específicos en las etiquetas `VALUE`, `JOBNAME`, `NODEID`, `CMDLINE`, entre otras, según el entorno (dev, int, au, qa, pro), y aplica una serie de validaciones y reglas configurables.

## 1. Requisitos previos
Antes de ejecutar el script, asegúrate de tener Python instalado y haber configurado el entorno correctamente.

## 2. Ejecución del Script
El script utiliza argparse para recibir los parámetros necesarios. A continuación, se muestra la forma de ejecución junto con los argumentos disponibles:

```bash
py lrba.py --ambiente <ambiente> --archivo-xml <archivo.xml> [opciones]
```

### 2.1 Argumentos obligatorios
--ambiente (str): Especifica el ambiente de destino. Opciones: 'dev', 'int', 'qa', 'au', 'pro'.
--archivo-xml (str): Especifica el nombre del archivo XML que se va a modificar (incluye la extensión .xml).
### 2.2 Opciones de modificación
--modificar-quantitative: Activa la modificación o agrega las etiquetas QUANTITATIVE en el archivo XML.
--modificar-domail: Activa la modificación o agrega las etiquetas DOMAIL, que suelen indicar la configuración de dominio para un ambiente específico.
--modificar-odate: Modifica las variables %%ODATE en el archivo XML, agregando '..' si es necesario para representar fechas operativas.
--modificar-jobs (str): Especifica los últimos dos caracteres de los JOBNAME a modificar, separados por comas (ejemplo: C01,D02,L03).
--dry-run: Ejecuta el script en modo simulación, sin realizar cambios permanentes en el archivo.

## 2.3 Ejemplos de ejecución
### 2.3.1 Ejemplos de simulación
- Ejemplo para el ambiente de Producción:

```bash
py lrba.py --ambiente pro --archivo-xml CR-COCBGHDIA-T03.xml --modificar-quantitative --modificar-domail --modificar-odate --modificar-jobs D01,C02 --dry-run
```

El cual generara el archivo CR-COCBGHDIA-T03-generate.xml en ambiente de producción

- Ejemplo para el ambiente de Calidad:

```bash
python lrba.py --ambiente qa --archivo-xml CR-COCBGHDIAC-T03.xml --modificar-quantitative --modificar-domail --modificar-odate --modificar-jobs L01,D02 --dry-run
```

El cual generara el archivo CR-COCBGHDIA-T03-generate.xml en ambiente de calidad

### 2.3.2 Ejemplos de ejecución
- Ejemplo para el ambiente de Producción:

```bash
py lrba.py --ambiente pro --archivo-xml CR-COCBGHDIA-T03.xml --modificar-quantitative --modificar-domail --modificar-odate --modificar-jobs D01,C02 --dry-run
```

El cual generara el archivo CR-COCBGHDIA-T03.xml en ambiente de producción

- Ejemplo para el ambiente de Calidad:

```bash
python lrba.py --ambiente qa --archivo-xml CR-COCBGHDIAC-T03.xml --modificar-quantitative --modificar-domail --modificar-odate --modificar-jobs L01,D02 --dry-run
```

El cual generara el archivo CR-COCBGHDIAC-T03.xml en ambiente de calidad

## 3. Buenas Prácticas
Backups del XML Original: Antes de realizar cambios en un archivo XML, realiza una copia de seguridad para poder restaurarlo en caso de ser necesario.
Validación Regular de Configuraciones: Es recomendable revisar y validar los valores de configuración en config.py periódicamente, ya que los entornos pueden cambiar con el tiempo.
Pruebas en Ambiente de Desarrollo: Ejecuta el script en un ambiente de pruebas antes de aplicarlo en producción para asegurarte de que los cambios funcionen correctamente.

## 4. Estructura del Proyecto
lrba.py: Archivo principal donde se ejecuta el programa y se aplican todas las modificaciones al archivo XML.
config.py: Archivo de configuración para las opciones de prefijos y variables de entorno específicas de cada ambiente (calidad y producción).
constants.py: Contiene constantes usadas en el programa, como nombres de etiquetas XML y otros valores.
logger_setup.py: Define la configuración para el sistema de logging, centralizando cómo se capturan, formatean y almacenan los mensajes de log.

## 5. Configuración del Logger
Los mensajes de log incluyen:
Fecha y Hora: Momento del evento.
Nombre del Logger: Identificación de origen del log dentro de la aplicación.
Nivel del Log: Severidad del mensaje (DEBUG, INFO, WARNING, ERROR, CRITICAL).
Mensaje: Descripción del evento.

Cada línea en el archivo de log tiene el formato:

```bash 
YYYY-MM-DD HH:MM:SS,ms - logger_name - SEVERITY_LEVEL - message
```

### 5.1 Detalles de Almacenamiento
Directorio de Logs: Los logs se guardan en una carpeta llamada log en el directorio de ejecución del script. Si no existe, el script la crea automáticamente.

Rotación de Archivos: El archivo de log tiene una capacidad máxima de 100 MB. Al superar este límite, se guarda hasta 5 versiones antiguas del archivo, manteniendo solo las más recientes.