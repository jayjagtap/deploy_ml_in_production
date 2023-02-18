import efficientnet.keras as efn
from tf.keras.applications.efficientnet import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np

class Efficient_Net():
    
    def __init__(self):
        self.model = efn.EfficientNetB3(input_shape = (224, 224, 3), include_top = False, weights = 'imagenet')
        
    def get_predictions(self, file_path):

        # Load a given image and preprocess it for efficientnet
        img = image.load_img(file_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x= np.array([x])
        x = preprocess_input(x)

        predictions  = self.model.predict(x)
        predictions = decode_predictions(preds, top=3)[0]

        return predictions