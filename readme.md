# StackIA

StackIA es un proyecto basado en contenedores que permite la predicción de números utilizando el dataset MNIST. La arquitectura del sistema está compuesta por varios contenedores que trabajan en conjunto para ofrecer una solución completa.

## Contenedores

### `apiia`
- Contenedor con una API desarrollada en Flask.
- Realiza la predicción de números utilizando el dataset MNIST.

### `web`
- Contenedor con una aplicación web desarrollada en Django.
- Permite cargar imágenes para su predicción y mostrar los resultados.
- Almacena los resultados predichos y las URLs de las imágenes cargadas en el contenedor `dbia`.

### `dbia`
- Contenedor con una base de datos PostgreSQL 13.
- Almacena la información gestionada desde el contenedor `web`.

## Instalación y uso

### Requisitos previos
Asegúrate de tener instalados los siguientes programas en tu sistema:
- Docker
- Docker Compose

### Pasos de instalación
1. Clona este repositorio:
   ```
   git clone https://github.com/EderLara/stackia.git
   cd stackia
   ```
2. Levanta los contenedores con Docker Compose:
    ```
    docker-compose up -d --build
    ```
3. Ingresa a la terminal del contenedor web:
    ```
    docker exec -it web bash
    ```
4. Aplica las migraciones de Django:
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```
5. Reinicia el contenedor ```web``` para aplicar los cambios:
    ```
    docker restart web
    ```

### Uso
* Accede a la interfaz web desde tu navegador en http://localhost:8000.
* Sube una imagen y obtén la predicción del número utilizando el modelo entrenado.
* Se te mostrará el resultado de la predicción.
* Consulta los resultados almacenados en la base de datos PostgreSQL.

## Licencia
Este proyecto está bajo la licencia MIT.



