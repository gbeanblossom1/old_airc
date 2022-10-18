from flask import Flask, Response
# Custom package to load machine learning model
#import tb_models
import json
import nltk
import os
#import sent2vec
import sys
import time


def create_app():
    app = Flask(__name__)

    from . import query
    from . import charts
    from . import schema
    app.register_blueprint(query.bp)
    app.register_blueprint(charts.bp)
    app.register_blueprint(schema.bp)

    # --- Set the application OS ---
    if sys.platform.startswith("win"):
        app.os = "windows"
    else:
        app.os = "*nix" 

    # Depending on OS, set paths to config file, global variables file, and sim search model
    if app.os == "windows":   
        config_path = os.getenv('TB_CONFIG')
        model_path = os.getenv('SIM_MODEL')
    else:
        config_path = "/opt/config/tb_config.json"
        model_path = "/opt/vector_model/wiki_unigrams.bin"

    # --- Configure application settings and global variables---
    with open(config_path) as config_file:
        app.settings = json.load(config_file)
    #from ..tb_models import 
    # --- Load model for similarity search ---
    #import models
    #app.model = models.getSent2Vec(model_path)

    # Setting to encode json responses as UTF-8
    app.config['JSON_AS_ASCII'] = False
    '''
    
    if app.os == "windows":
        model_path = os.getenv('SIM_MODEL')
    else:
        model_path = "/opt/models/sim_model.bin"
    print('loading model')
    start = time.time()
    app.sim_model = tb_models.getSent2Vec(model_path)
    print('loaded model')
    print( (time.time() - start) / 60)
    '''
    # --- Configure root URL response ---
    @app.route('/')
    def root():
        info = """{ "features" : [ 
                        { "path" : "/query", 
                        "description" : "This collection of endpoints is used to query the elastic search DB through the ThreatBeacon API."},
                        { "path" : "/schema",
                        "description" : "This collection of endpoints is used to provide schemas to other endpoints throughout the API. Just add '/schema' to the beginning of the URL path."}
                        ]
                    }"""
        return Response(info, mimetype="application/json")
        return app.name

    return app


