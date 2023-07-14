import tensorflow as tf
import os

class Model():
    def __init__(self, checkpoint):
        self.model = tf.keras.models.load_model(os.path.join('vfonly/weights', checkpoint), compile = False)
    def predict(self, x):
        # y = self.model.predict(x, batch_size=1, verbose=0)
        y = self.model(x, training=False).numpy()
        return y