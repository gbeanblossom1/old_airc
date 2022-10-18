from flask import Blueprint
from flask import request
from flask import jsonify
from flask import Response
from flask import current_app as app
#from elastipy import search, queryBuilder
#import query_utils as utils
#from query import query_helpers as helpers
from query import query_helpers as helpers
from query import query_charts as charts
#from ..generic_utils import generic_helpers
import json, os, sys

bp = Blueprint('query', __name__, url_prefix="/query")

@bp.route('/sql_search', methods=("POST",))
def sql_search():
    #response = generic_helpers.set_endpoint_response()

    ##############
    # VALIDATION #
    ##############
    json_body = request.get_json()
    query = json_body.get('query_text')
    ##########
    # SEARCH #
    ##########
    func_response = json.loads(open("sample_data.json").read())[:100]
    chart_data = charts.generate_charts(func_response)

    return_response = {"status": 200, "message": "", "results": func_response, "charts": chart_data}
    return Response(json.dumps(return_response), status=200, mimetype='application/json')

    ###################
    # PROCESS RESULTS #
    ###################



@bp.route('/', methods=("GET",))
def root():
    info = """{ "endpoints" : [
                { "path" : "/document_count", 
                "methods" : "GET",
                "params" : {},
                "schema" : "/schema/query/document_count" },
                { "path" : "/search_basic",  
                "methods" : "GET",
                "params" : {
                    "required" : [
                        {"name": "data_types", "type": "string", "description": "A comma-separated string of data types", "enum": ["Publications", "Patents", "Companies", "Grants"]}, 
                        {"name": "category", "type": "string", "description": "A field category that defines which fields will be searched on", "enum": ["Documents", "People", "Institutions"]}, 
                        {"name": "query_text", "type": "string", "description": "The query string to use for search"}, 
                        {"name": "page_size", "type": "integer", "description": "The number of documents to return for each data type", "minimum": 0, "maximum": 10000},
                        {"name": "start_year", "type": "integer", "description": "The lowest year to filter your search on", "minimum": 1600, "maximum": 2020},
                        {"name": "end_year", "type": "integer", "description": "The highest year to filter your search on", "minimum": 1600, "maximum": 2020}],
                    "optional" : [
                        {"name": "page_number", "type": "integer", "description": "The page of results to collect. This value is 0-indexed. If not provided, this value is set to 0"}, 
                        {"name": "filters", "type": "object", "description": "A mapping of key/value pairs that specifies the fields to filter on and their filter values. If not provided, no filters are applied"}] } },
                { "path" : "/search_similarity",
                "methods" : "GET",
                "params" : "Coming soon." }
            ] }"""
    return Response(info, mimetype="application/json")