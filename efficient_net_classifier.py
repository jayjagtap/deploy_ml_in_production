import tensorflow as tf
import tensorflow.keras.applications.efficientnet as efn
from tensorflow.keras.applications.efficientnet import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np

class Efn_classifier():
    
    def __init__(self):
        self.model = tf.keras.applications.efficientnet.EfficientNetB7(
                        include_top=True,
                        weights='imagenet',
                        input_tensor=None,
                        input_shape=None,
                        pooling=None,
                        classes=1000,
                        classifier_activation='softmax',
                    )
        
    def get_predictions(self, file_path):

        # Load a given image and preprocess it for efficientnet
        img = image.load_img(file_path, target_size=(600, 600))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        # Inference
        features = self.model.predict(x)
        predictions = decode_predictions(features, top=3)[0]

        return predictions