from django.shortcuts import render                 # Para renderizar la plantilla
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib import messages                 # Para mostrar mensajes de error al usuario
import requests
import os
import logging                                      # Es buena práctica usar logging

from .forms import PrediccionForm
from .models import Prediccion

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar la URL de la API desde variables de entorno
model_api_url = os.getenv('MODEL_API_URL')
if not model_api_url:
    logger.error("La variable de entorno MODEL_API_URL no está configurada.")

class PrediccionView(TemplateView):
    template_name = 'predicciones/prediccion.html'
    formulario = PrediccionForm 

    def get_context_data(self, **kwargs):
        """Añade el formulario al contexto."""
        context = super().get_context_data(**kwargs)
        if 'formulario' not in context:                             # Si no viene de un POST fallido
             context['formulario'] = self.formulario()
        
        # Manejar parámetro GET si aún lo necesitas
        prediccion_param = self.request.GET.get('prediccion')
        if prediccion_param:
            context['mensaje_url'] = f"Mensaje desde la URL: {prediccion_param}"

        return context

    def post(self, request, *args, **kwargs):
        """Maneja el envío del formulario."""
        form = self.formulario(request.POST, request.FILES)
        context = self.get_context_data() # Obtener contexto base
        context['formulario'] = form # Actualizar con el form enviado (incluye errores si los hay)

        if form.is_valid():
            image_file = form.cleaned_data['imagen'] # Obtener el archivo subido

            # --- Llamada directa a la API con el archivo original ---
            if not model_api_url:
                 messages.error(request, "La configuración del servidor para la predicción no está completa.")
                 return render(request, self.template_name, context)

            try:
                logger.debug(f"Intentando enviar archivo '{image_file.name}' a {model_api_url}")
                
                # Prepara el payload para 'files'. La clave DEBE ser 'imagen'.
                # Pasamos el objeto de archivo directamente. requests se encarga del resto.
                files_payload = {'imagen': (image_file.name, image_file.read(), image_file.content_type)}

                # Realizar la petición POST a la API del modelo
                response = requests.post(model_api_url, files=files_payload, timeout=20) # Timeout por si el modelo tarda

                # Lanza una excepción para respuestas de error (4xx o 5xx)
                response.raise_for_status()

                logger.info(f"Llamada a API exitosa (Status: {response.status_code})")
                prediction_data = response.json()
                predicted_class = prediction_data.get('predicted_class')
                confidence = prediction_data.get('confidence')

                # --- Guardar en Base de Datos DESPUÉS de obtener predicción ---
                # Es mejor guardar solo si la predicción fue exitosa
                if predicted_class is not None and confidence is not None:
                    # Crear y guardar la instancia Prediccion
                    # Necesitamos volver al inicio del archivo para guardarlo correctamente
                    image_file.seek(0)
                    prediccion = Prediccion(
                        imagen=image_file,                                      # Guardar el archivo original
                        prediccion=predicted_class,
                        confianza=confidence
                    )
                    # Actualizar contexto para mostrar resultados
                    context['prediccion'] = predicted_class                     # Clase predicha (índice)
                    context['confianza'] = confidence                           # Clase predicha (índice)
                    context['imagen_url'] = prediccion.imagen                   # Clase predicha (índice) 

                    if prediccion:
                        logger.debug(f"Guardando predicción: {prediccion}")
                    else:
                        logger.error("Error al crear la instancia de Prediccion.")
                        messages.error(request, "Error al crear la predicción en la base de datos.")
                        return render(request, self.template_name, context)
                    
                    prediccion.save()
                    logger.info(f"Predicción {prediccion.id} guardada en BD.")
                    messages.success(request, f"Predicción realizada con éxito.")                                # Mensaje de éxito                                         
                    
                else:
                    logger.error(f"La respuesta de la API no contenía los datos esperados: {prediction_data}")
                    messages.error(request, "La respuesta del servicio de predicción fue incompleta.")

            except requests.exceptions.HTTPError as http_err:
                status_code = http_err.response.status_code
                error_text = http_err.response.text
                logger.error(f"Error HTTP {status_code} al llamar a la API: {error_text}", exc_info=True)
                # Intentar parsear el JSON de error de Flask si existe
                try:
                    error_details = http_err.response.json().get('error', 'Detalle no disponible')
                except ValueError:
                    error_details = error_text or 'Sin detalles adicionales.'
                messages.error(request, f"Error ({status_code}) al contactar el servicio de predicción: {error_details}")

            except requests.exceptions.RequestException as req_err:
                logger.error(f"Error de red al llamar a la API: {req_err}", exc_info=True)
                messages.error(request, f"No se pudo conectar con el servicio de predicción: {req_err}")

            except Exception as e:
                # Captura cualquier otro error inesperado (ej: error al guardar en BD)
                logger.error(f"Error inesperado en el proceso POST: {e}", exc_info=True)
                messages.error(request, f"Ocurrió un error inesperado: {e}")

            # Renderizar la plantilla con el contexto actualizado (resultados o errores)
            return render(request, self.template_name, context)

        else: # El formulario no es válido
            logger.warning(f"Formulario inválido: {form.errors}")
            messages.warning(request, "Por favor, corrige los errores en el formulario.")
            # Renderizar la plantilla con el formulario inválido (ya está en el contexto)
            return render(request, self.template_name, context)