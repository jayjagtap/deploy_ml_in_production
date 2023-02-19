# deploy_ml_in_production
Templates directory: Flask recognizeds this to contain html code
static directory: Flask recognizes this to contain CSS, JS code
app.py : This file is the root of our Flask application. We define all the routes and functions to perform for each action.
app_helper.py : Calls the Tensorflow model to get predictions
efficient_net.py: Class to create TF model and load effiecientnet weights.