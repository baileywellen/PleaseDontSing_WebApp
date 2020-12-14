#Configuration File for the Flask WebApp
import os 

#create a class called Config
class Config(object):
    #confirm that nothing has been altered or hacked
    SECRET_KY = os.environ.get('SECRET_KEY') or "secret_string"
    