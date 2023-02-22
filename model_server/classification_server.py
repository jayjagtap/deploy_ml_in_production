import tensorflow as tf
import tensorflow.keras.applications.efficientnet as efn
from tensorflow.keras.applications.efficientnet import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from tensorflow.python.keras.backend import set_session
from io import BytesIO
from PIL import Image
import threading
import zmq
from base64 import b64decode
import numpy as np
import logging
# Create and configure the logger
logging.basicConfig(
    level=logging.DEBUG,  # or logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
)

class Efn_classifier():
    
    def __init__(self):
        self.model = tf.keras.applications.efficientnet.EfficientNetB1(
                        include_top=True,
                        weights='imagenet',
                        input_tensor=None,
                        input_shape=None,
                        pooling=None,
                        classes=1000,
                        classifier_activation='softmax',
                    )


class Server(threading.Thread):
    def __init__(self):
        self._stop = threading.Event()
        threading.Thread.__init__(self)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        context = zmq.Context()

        # Create ZeroMQ socket of type ROUTER: Load Balancer distributes incoming messages
        frontend = context.socket(zmq.ROUTER)
        frontend.bind('tcp://*:7777')

        # Create ZeroMQ socket of type DEALER: Worker thread
        backend = context.socket(zmq.DEALER)
        backend.bind('inproc://backend_endpoint')

        poll = zmq.Poller()
        poll.register(frontend, zmq.POLLIN)
        poll.register(backend,  zmq.POLLIN)

        while not self.stopped():
            sockets = dict(poll.poll())
            if frontend in sockets:
                if sockets[frontend] == zmq.POLLIN:
                    _id = frontend.recv()
                    json_msg = frontend.recv_json()

                    handler = RequestHandler(context, _id, json_msg)
                    handler.start()

            if backend in sockets:
                if sockets[backend] == zmq.POLLIN:
                    _id = backend.recv()
                    msg = backend.recv()
                    frontend.send(_id, zmq.SNDMORE)
                    frontend.send(msg)

        frontend.close()
        backend.close()
        context.term()


class RequestHandler(threading.Thread):
    def __init__(self, context, id, msg):

        """
        RequestHandler
        :param context: ZeroMQ context
        :param id: Requires the identity frame to include in the reply so that it will be properly routed
        :param msg: Message payload for the worker to process
        """

        threading.Thread.__init__(self)
        logging.info("--------------------Entered requesthandler--------------------")
        self.context = context
        self.msg = msg
        self._id = id
        logging.info(f"Context: {self.context}, id: {self._id}")


    def process(self, obj):

        imgstr = obj['payload']
        img_bytes = b64decode(imgstr)
        img = Image.open(BytesIO(img_bytes))

        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # resize the input image and preprocess it
        img = img.resize((240,240))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)

        predictions = model.predict(img)

        predictions = decode_predictions(predictions, top=3)[0]
        logging.info(f"Predictions from class_model_server.py: {predictions}", )

        pred_strings = []
        for _,pred_class,pred_prob in predictions:
            pred_strings.append(str(pred_class).strip()+" : "+str(round(pred_prob,5)).strip())
        preds = ", ".join(pred_strings)

        return_dict = {}
        return_dict["preds"] = preds
        return return_dict

    def run(self):
        # Worker will process the task and then send the reply back to the DEALER backend socket via inproc
        worker = self.context.socket(zmq.DEALER)
        worker.connect('inproc://backend_endpoint')
        logging.info(f'Request handler started to process {self.msg.keys()}')

        # Simulate a long-running operation
        output = self.process(self.msg)

        worker.send(self._id, zmq.SNDMORE)
        worker.send_json(output)
        del self.msg

        logging.info('Request handler quitting.\n')
        worker.close()

classifier = Efn_classifier()
model = classifier.model

def main():
    # Start the server that will handle incoming requests
    server = Server()
    server.start()

if __name__ == '__main__':
    main()

"""
Notes

1. ZeroMQ
The Router-Dealer pattern is another messaging pattern in ZeroMQ that is commonly 
used for high-performance and scalable distributed systems. The pattern is often 
used for load-balancing and task distribution in a cluster of nodes.

In this pattern, the Router and Dealer sockets are used in combination to create
a scalable, asynchronous message passing system.

The Router socket is used as a load balancer, which distributes incoming messages to the various Dealer sockets that are connected to it. 
Each Dealer socket represents a worker node that is capable of handling tasks.

2. Thread class

start(): Calls run() method
run(): Listen to port, direct requests to request handler and terminate
"""
