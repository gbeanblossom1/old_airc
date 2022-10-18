import os
from flask import Flask
from flask import Response
import json
import os
import sys
import query
import views
#import charts
#import schema

app = Flask(__name__)

app.register_blueprint(query.bp)
app.register_blueprint(views.bp)
#app.register_blueprint(charts.bp)
#app.register_blueprint(schema.bp)

# --- Set the application OS ---
if sys.platform.startswith("win"):
    app.os = "windows"
else:
    app.os = "*nix"

    # Depending on OS, set paths to config file, global variables file, and sim search model
#if app.os == "windows":
#    config_path = os.getenv('TB_CONFIG')
#    model_path = os.getenv('SIM_MODEL')
#else:
#    config_path = "/opt/config/tb_config.json"
#    model_path = "/opt/vector_model/wiki_unigrams.bin"
config_path = "../tb_config_example.json"

# --- Configure application settings and global variables---
with open(config_path) as config_file:
    app.settings = json.load(config_file)
# from ..tb_models import
# --- Load model for similarity search ---
# import models
# app.model = models.getSent2Vec(model_path)

# Setting to encode json responses as UTF-8
app.config['JSON_AS_ASCII'] = False

if __name__ == "__main__":
    app.run(debug=True)