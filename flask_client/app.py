"""
app.py is the root of our Flask application. We define all the routes and functions to 
perform for each action.
"""

from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
from base64 import b64encode
import uuid
import zmq
import socket

# Define a flask app
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/uploader', methods = ['POST'])
def upload_file():
    predictions=""
    if request.method == 'POST':
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'static','uploads', secure_filename(f.filename))
        f.save(file_path)

        global img_str

        with open(file_path, "rb") as image_file:
            img_str = b64encode(image_file.read())
        img_str_json = img_str.decode('utf-8')

        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        _rid = "{}".format(str(uuid.uuid4()))
        socket.setsockopt_string(zmq.IDENTITY, _rid)
        socket.connect('tcp://localhost:5576')
        
        poll = zmq.Poller()
        poll.register(socket, zmq.POLLIN)
        socket.send_json({"payload": img_str_json, "_rid": _rid})

        received_reply = False
        while not received_reply:
            sockets = dict(poll.poll(1000))
            if socket in sockets:
                if sockets[socket] == zmq.POLLIN:
                    result_dict = socket.recv_json()                    
                    predictions = result_dict['preds']
                    received_reply = True                    
                    return render_template("upload.html", predictions=predictions, display_image=f.filename) 

        socket.close()
        context.term()
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=9000) # Test on PC
    # app.run()