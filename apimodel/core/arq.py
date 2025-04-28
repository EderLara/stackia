import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt

""" Paso 1 Cargar el Conjunto de Datos MNIST: """
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

""" Paso 2 Preprocesar los Datos: """
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
input_shape = (784,)
x_train = x_train.reshape(x_train.shape[0], 784)
x_test = x_test.reshape(x_test.shape[0], 784)
num_classes = 10
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

""" Paso 3 Definir la Arquitectura de la Red Neuronal: """
model = keras.Sequential(
    [
        layers.Input(shape=input_shape),
        layers.Dense(128, activation="relu"),
        layers.Dense(num_classes, activation="softmax"),
    ]
)

# Mostrar la arquitectura del modelo
model.summary()

""" Paso 4 Compilar el Modelo: """
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

""" Paso 5 Entrenar la Red (y Guardar el Mejor Modelo) """
batch_size = 128
epochs = 10

# Definir el callback ModelCheckpoint
filepath = '../model/best_mnist_model.h5'

checkpoint_callback = keras.callbacks.ModelCheckpoint(
    filepath=filepath,
    save_best_only=True,
    monitor='val_loss',     # Monitorea la pérdida en el conjunto de validación
    verbose=1               # Muestra mensajes cuando se guarda el modelo
)

# Entrenar el modelo pasando el callback
history = model.fit(
    x_train,
    y_train,
    batch_size=batch_size,
    epochs=epochs,
    validation_split=0.1,
    callbacks=[checkpoint_callback]  # <--- ¡Aquí es donde se pasa el callback!
)

""" Paso 6 Evaluar el Modelo (Cargando el Mejor Modelo Guardado) """
# Cargar el mejor modelo guardado
loaded_model = keras.models.load_model(filepath)

# Evaluar el modelo cargado en el conjunto de prueba
score = loaded_model.evaluate(x_test, y_test, verbose=0)
print("Pérdida en el conjunto de prueba (mejor modelo):", score[0])
print("Precisión en el conjunto de prueba (mejor modelo):", score[1])

