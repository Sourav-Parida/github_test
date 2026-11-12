
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input,Rescaling,Conv2D,MaxPooling2D,Flatten,Dense



# 1. Load Fashion MNIST dataset
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()

# # 2. Reshape images
x_train = x_train.reshape(-1, 28, 28, 1)
x_test = x_test.reshape(-1, 28, 28, 1)

# 3. Create CNN model

model= tf.keras.Sequential()
model.add(Input(shape=(28, 28, 1)))
model.add(Rescaling(1./255))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(10, activation='softmax'))


# 4. Compile model
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 5. Train model
model.fit(
    x_train,
    y_train,
    epochs=10,
    batch_size=32,
    validation_split=0.2
)

# 6. Evaluate model
loss, accuracy = model.evaluate(x_test, y_test)

print("Test Loss:", loss)
print("Test Accuracy:", accuracy)

# # 7. Predict an image
# prediction = model.predict(x_test[:1])

# predicted_class = np.argmax(prediction)

# # 8. Fashion MNIST class names
# class_names = [
#     'T-shirt/top',
#     'Trouser',
#     'Pullover',
#     'Dress',
#     'Coat',
#     'Sandal',
#     'Shirt',
#     'Sneaker',
#     'Bag',
#     'Ankle boot'
# ]

# print("Predicted:", class_names[predicted_class])
# print("Actual:", class_names[y_test[0]])





