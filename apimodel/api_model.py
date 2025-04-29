from flask import Flask, request, jsonify
from PIL import Image, ImageOps # Importar ImageOps para la inversión
import numpy as np
import tensorflow as tf
import io
import os
import logging # Añadir logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG) # Configurar logging básico

# Cargar el modelo (asegúrate de que la ruta sea correcta dentro del contenedor)
MODEL_PATH = './model/best_mnist_model.h5' # Asumiendo que esta es la ruta correcta en el contenedor
if not os.path.exists(MODEL_PATH):
    logging.error(f"Error Crítico: Modelo no encontrado en {MODEL_PATH}")
    # Considera una forma más robusta de manejar esto si la API no puede funcionar sin el modelo
    exit() # O manejar el error de forma diferente

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    # Opcional: Compilar métricas si es necesario para alguna funcionalidad específica,
    # aunque para 'predict' no suele ser estrictamente necesario.
    # model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    logging.info(f"Modelo cargado exitosamente desde {MODEL_PATH}")
except Exception as e:
    logging.error(f"Error al cargar el modelo desde {MODEL_PATH}: {e}", exc_info=True)
    # Manejar el error apropiadamente, quizás la API no debería iniciar.
    exit()

# Umbral para determinar si el fondo es claro u oscuro
# Un valor por encima de este umbral sugiere un fondo blanco (o claro)
# Un valor por debajo sugiere un fondo negro (o oscuro)
# 128 es el punto medio entre 0 (negro) y 255 (blanco).
# Puedes ajustar este valor si es necesario basándote en tus imágenes.
INVERSION_THRESHOLD = 128

def preprocess_image(image_bytes):
    """
    funcion para preprocesar la imagen, se carga y se valida si hay que invertirle los colores
    """
    try:
        logging.debug("Procesando imagen recibida...")
        # 1. Abrir imagen y convertir a escala de grises ('L')
        img = Image.open(io.BytesIO(image_bytes)).convert('L')
        logging.debug(f"Imagen abierta. Modo: {img.mode}, Tamaño: {img.size}")

        # 2. Redimensionar a 28x28 píxeles (tamaño MNIST)
        img = img.resize((28, 28), Image.Resampling.LANCZOS) # Usar un método de remuestreo explícito
        logging.debug(f"Imagen redimensionada a {img.size}")

        # 3. Convertir a array NumPy temporalmente para calcular la media ANTES de normalizar/invertir
        img_array_raw = np.array(img)
        mean_pixel_value = np.mean(img_array_raw)
        logging.debug(f"Valor medio de píxeles (antes de normalizar/invertir): {mean_pixel_value:.2f}")

        # 4. *** ¡INVERSIÓN CONDICIONAL DE COLORES! ***
        # Si la media es alta (fondo claro), invertir la imagen.hje6
        if mean_pixel_value > INVERSION_THRESHOLD:
            logging.debug("Detectado fondo claro (media > umbral). Invirtiendo colores...")
            img = ImageOps.invert(img) # Invertir la imagen PIL original
            img_array_processed = np.array(img) # Convertir la imagen invertida a array
            logging.debug("Colores invertidos (fondo negro, dígito blanco).")
        else:
            logging.debug("Detectado fondo oscuro (media <= umbral). Omitiendo inversión.")
            img_array_processed = img_array_raw # Usar el array original (no invertido)
            logging.debug("Colores no invertidos.")

        # 5. Normalizar (valores entre 0 y 1)
        # img_array_processed ahora contiene la imagen en el formato deseado (fondo negro, dígito blanco)
        img_array_normalized = img_array_processed / 255.0
        logging.debug(f"Imagen convertida a array NumPy y normalizada. Forma: {img_array_normalized.shape}, Rango: [{img_array_normalized.min()}-{img_array_normalized.max()}]")

        # 6. Reformatear para el modelo (1 muestra, 784 características)
        # Asegúrate que tu modelo espera un vector plano de 784 o una imagen 2D/3D
        # Si espera (1, 28, 28, 1) o (1, 28, 28), ajusta el reshape.
        # Este reshape asume que el modelo espera un vector plano (784,).
        # img_array_reshaped = img_array_normalized.reshape(1, 784) -> 
        img_array_reshaped = img_array_normalized.reshape(1,28,28,1) # 1, la cantida de muestras, 28,28, es la dimension, 1 la cantidad de muestras
        logging.debug(f"Array reformateado a: {img_array_reshaped.shape}")

        return img_array_reshaped
    except Exception as e:
        logging.error(f"Error durante el preprocesamiento de la imagen: {e}", exc_info=True)
        raise # Relanzar la excepción para que sea manejada en la ruta


@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint para recibir una imagen y devolver la predicción del modelo."""
    logging.info(f"Solicitud POST recibida en /predict desde {request.remote_addr}")
    if 'imagen' not in request.files:
        logging.warning("Solicitud recibida sin archivo en el campo 'imagen'.")
        return jsonify({'error': 'No se proporcionó ninguna imagen en el campo "imagen"'}), 400

    image_file = request.files['imagen']
    logging.debug(f"Archivo recibido: {image_file.filename}, Tipo: {image_file.content_type}")

    try:
        # Leer los bytes del archivo
        image_bytes = image_file.read()
        if not image_bytes:
             logging.warning("El archivo recibido está vacío.")
             return jsonify({'error': 'El archivo de imagen está vacío'}), 400

        # Preprocesar la imagen (incluye la inversión CONDICIONAL)
        processed_image = preprocess_image(image_bytes)

        # Realizar la predicción
        logging.debug("Realizando predicción con el modelo...")
        predictions = model.predict(processed_image)
        logging.debug(f"Predicciones crudas (logits/probabilidades): {predictions}")

        # Obtener la clase predicha (índice con mayor probabilidad) y la confianza
        predicted_class = np.argmax(predictions[0])
        confidence = np.max(predictions[0])

        logging.info(f"Predicción: Clase={predicted_class}, Confianza={confidence:.4f}")

        # Devolver el resultado como JSON
        return jsonify({
            'predicted_class': int(predicted_class),        # Convertir a int para JSON
            'confidence': float(confidence) * 100           # Convertir a porcentaje
        })

    except FileNotFoundError as fnf_error:
          logging.error(f"Error crítico: {fnf_error}", exc_info=True)
          return jsonify({'error': 'Error interno del servidor: Falta archivo de modelo'}), 500
    except Exception as e:
        logging.error(f"Error durante la predicción o preprocesamiento: {e}", exc_info=True)

        return jsonify({'error': 'Error interno al procesar la imagen o realizar la predicción'}), 500

if __name__ == '__main__':
    # Usar host='0.0.0.0' para que sea accesible desde fuera del contenedor
    # debug=False es generalmente recomendado para producción/staging
    app.run(host='0.0.0.0', port=5000, debug=False)