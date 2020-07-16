#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template
from flask import Flask, flash, request, redirect, url_for, json
from werkzeug.utils import secure_filename
import io
import tensorflow as tf
import numpy as np
from keras.models import model_from_json
from PIL import Image
import os

ALLOWED_EXTENSIONS = {'jpg','png','jpeg'}
LABELS  = ["White","Black","Asian","Indian","Other"]
app = Flask(__name__,static_url_path='/static')
model = None
graph = None


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def compile_model():
    global model
    json_file = open(os.getenv('NN_MODEL', 'model.json'), 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into new model
    model.load_weights(os.getenv('NN_WEIGHTS', 'test.hdf5'))
    print("Loaded model from disk")

    model.compile(
        optimizer= "adam",
        loss= "mse")

    global graph
    graph = tf.get_default_graph() 


@app.route('/predict',methods=['POST'])
def predict():
   
    file = request.files['file']
    if file.filename == '':
        response = app.response_class(
            response=json.dumps({"error":"No selected file"}),
            status=401,
            mimetype='application/json'
        )
        return response


    if file and allowed_file(file.filename):
        img = Image.open(io.BytesIO(file.stream.read()))
        img = img.resize((64,64), Image.ANTIALIAS)
        data = np.asarray( img, dtype="int32" )
        x = data[...,:3]

        global model
        global graph

        with graph.as_default():
            prediction= model.predict(x[np.newaxis,...])[0]


        response = app.response_class(
            response=json.dumps({"prediction":{ k:round(v*100,2) for k,v in zip(LABELS,prediction)}}),
            status=201,
            mimetype='application/json'
        )
        return response

    response = app.response_class(
            response=json.dumps({"error":"No allowed file"}),
            status=404,
            mimetype='application/json'
        )
    return response


@app.route('/', methods=['GET'])
def upload_file():
    return render_template('index.html')


compile_model()
if __name__ == '__main__':
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'O$%7kQgXKVOhT@refsbY;mQmt9lMWg')
    port = os.getenv('PORT', 8000)
    print('port=', port)
    app.run(host='0.0.0.0', debug=True, port=port)
