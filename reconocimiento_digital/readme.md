# Guia de instalación de Django==5.2

## Crear un entorno virtual
~~~
python -m venv iaenv
~~~

## Activar entorno virtua (en Win):
~~~
.\iaenv\Scripts\activate
~~~

## Instalar librerías
~~~
pip install Django==5.2 Pillow Dotenv
~~~

## Crear proyecto en django
(iaenv) C:\devpython\reconocimiento digital>..\iaenv\Scripts\django-admin.exe starproject src

## Crear aplicaciones en django:

~~~
 (iaenv) C:\devpython\reconocimiento digital>python manage.py startapp predicciones
 (iaenv) C:\devpython\reconocimiento digital>python manage.py startapp reportes
~~~

# Crear modelo de datos de la aplicación:
1. crear la clase: class Prediccion(models.Model): ...

# Adicionar a admin.py de la aplicacion
1. registrar el modelo de datos en el archivo admin.py de la aplicacion

## Ejecutar para utilizar base de datos:
~~~
 (iaenv) C:\devpython\reconocimiento digital>python manage.py makemigrations predicciones reportes
 (iaenv) C:\devpython\reconocimiento digital>python manage.py migrate
~~~

## Ejecutar para iniciar la aplicacion:

~~~
 (env) C:\devpython\reconocimiento digital>python manage.py runserver
~~~

# Pasos a seguir:

* Continuar creando aplicaciones, con sus modelos, luego crear templates

~~~
 (env) C:\devpython\reconocimiento digital>python manage.py startapp ...
 """ Crear modelos, formularios, agregar al admin.py ...etc. """
~~~