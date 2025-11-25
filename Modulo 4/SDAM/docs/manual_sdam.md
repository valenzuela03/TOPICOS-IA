# Manual de Usuario de SDAM

Este manual proporciona una guía paso a paso para la instalación y
operación del **Sistema de Detección y Asociación de Matrículas
(SDAM)**, el cual identifica vehículos en tiempo real y vincula con la base de datosde propietarios.

## 1. Requisitos y Preparación

Para iniciar el sistema debe de cumplir con los siguientes
requisitos:

-   **Cámara Web (Webcam):** Necesita una cámara web funcional conectada
    a su PC.\
-   **Entorno Python:** Debe tener **Python 3.9+** y el entorno virtual
    (`venv/`) activado.\
-   **Base de Datos:** El archivo `db/matriculas.db` debe existir e
    inicializarse.
    -   Ejecute:

        ``` bash
        python3 src/linking_system/setup_db.py
        ```

### 1.1 Crear e Instalar el Entorno Virtual (venv)

**Crear el entorno:**

``` bash
python3 -m venv venv
```

**Activar el entorno:**

-   **MacOS**

    ``` bash
    source venv/bin/activate
    ```

**Instalar dependencias:**

``` bash
pip3 install -r requirements.txt
```

### 1.2 Activa el Entorno

Se debe de activar el entorno virtual siempre antes de ejecutar cualquier script si no no correra el sistema:

-   **MacOS**

    ``` bash
    source venv/bin/activate
    ```

## 2. Operación del Sistema en Tiempo Real

El sistema SDAM se ejecuta desde la línea de comandos y abre una ventana
de video en vivo.

### 2.1 Iniciar el Sistema

Ejecute el script principal:

``` bash
python src/main.py
```

### 2.2 Interfaz de la Ventana de Video

  ---------------------------------------- ------------------------------
  **Recuadro Verde**                       
  Placa detectada. YOLOv8 la ha localizado con alta confianza.

  **Texto Verde (parte inferior)**         
  Placa registrada en la base de datos.

  **Texto Rojo (parte inferior)**         
  Placa no registrada.

  -----------------------------------------------------------------------

### 2.3 Finalizar la Operación

Presionar la tecla `q` en la ventana de video para cerrar el sistema.

## 3. Administración de Datos

### 3.1 Agregar Nuevos Propietarios y Vehículos

1.  Edite `add_new_owner.py`.\
2.  Ejecutar:

``` bash
python add_new_owner.py
```

------------------------------------------------------------------------

## 4. Solución de Problemas Comunes

  ------------------ --------------------------------- -----------------------
  La cámara no sabre.      
  Verifique uso por otras apps.

  Detección lenta Retraso o parpadeo.                
  Cierre apps pesadas.

  OCR incorrecto o texto mal leído.
  Ajuste iluminación o distancia.

  DB no encontrada.
  Ejecutar setup_db.py

  Falta dependencia  paddleocr faltante                Activar venv e instalar requerimientos
  
  ----------------------------------------------------------------------------
