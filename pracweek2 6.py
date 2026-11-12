import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)
fashion_mnist=tf.keras.datasets.fashion_mnist
(X_train,y_train),(X_test,y_test)=fashion_mnist.load_data()

print("Training images:", X_train.shape)
print("Training labels:", y_train.shape)
print("Test images:", X_test.shape)
print("Test labels:", y_test.shape)

#normalize 
X_train=X_train/255
X_test=X_test/255
X_train=X_train.reshape(-1,28,28,1)
X_test=X_test.reshape(-1,28,28,1)
print("Training images:", X_train.shape)
print("Test images:", X_test.shape)

fashion_model=tf.keras.Sequential([
    tf.keras.layers.Input(shape=(28,28,1)),
    tf.keras.layers.Conv2D(32,(3,3),activation="relu"),
    tf.keras.layers.MaxPool2D((2,2)),
    tf.keras.layers.Conv2D(64,(3,3),activation="relu"),
    tf.keras.layers.MaxPool2D((2,2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128,activation="relu"),
    tf.keras.layers.Dense(10,activation="softmax")
      
])


fashion_model.summary()
fashion_model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)
fashion_model.fit(
    X_train,
    y_train,
    epochs=10,
    batch_size=64,
    validation_split=0.2
)
fashion_test_loss, fashion_test_accuracy = fashion_model.evaluate(
    X_test, y_test, verbose=0
)

print(f"Test loss: {fashion_test_loss:.4f}")
print(f"Test accuracy: {fashion_test_accuracy:.4f}")
fashion_probabilities = fashion_model.predict(X_test, verbose=0)
fashion_predictions = np.argmax(fashion_probabilities, axis=1)


fashion_cm = confusion_matrix(y_test, fashion_predictions)
print(classification_report(
    y_test,
    
    fashion_predictions,
   
    zero_division=0
))
