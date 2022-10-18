from flask import Blueprint, request, jsonify, Response
from flask import current_app as app

bp = Blueprint('schema', __name__, url_prefix="/schema")


@bp.route('/', methods=("GET",))
def root():
    info = """{ "endpoints" : [ 
                    { "path" : "/schema/query/document_count", 
                    "methods" : "GET",
                    "params" : {} }
                ]  
            }"""
    return Response(info, mimetype="application/json")


@bp.route('/query/document_count', methods=("GET",))
def doc_count():
  api_url = "/query/document_count"
  schema_url = "/schema/document_count"
  title = "Document Count"
  properties = """{"success":
                {"type":"boolean",
                "description":"True if request was successful, otherwise an error has occurred"},
                "message":{"type":"string",
                "description":"The error message if an error has occurred, otherwise empty string"},
                "status_code":{"type":"integer","description":"The status code of the returned response"},
                "results":{"type":"array","items":{"$ref":"#/definitions/doc_count_obj"}}}"""

  definitions = """{"doc_count_obj":
                {"type":"object",
                "required":["key", "label","value"],
                "properties": 
                {"key": {"type":"string", "description": "The key used to identify which source or title is returned"}
                "label":{"type":"string","description":"Display label"},
                "value":{"type":"integer","description":"The document count value"}}}}"""

  return Response(schema_template(api_url, schema_url, title, properties, definitions), mimetype='application/schema+json')


def schema_template(function_url, schema_url, object_title, properties, definitions=None):
    schema = f"""{{ "$id": "{function_url}",  
            "$schema": "{schema_url}",  
            "title": "{object_title}",  
            "type": "object",  
            "properties":  {properties} , 
            "definitions": {definitions} }}"""

    return schema
