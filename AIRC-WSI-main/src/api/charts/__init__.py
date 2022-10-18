from flask import Blueprint, request, jsonify, Response
from flask import current_app as app
from elastipy import search, queryBuilder
from ..query import query_utils
#from ..query import query_helpers as helpers
from . import chart_utils
# Generic helper functions
from ..generic_utils import generic_helpers

bp = Blueprint('charts', __name__, url_prefix="/charts")

@bp.route('/chart_view', methods=("POST",))
def create_charts():
	response = generic_helpers.set_endpoint_response()
	# Set es_client variable in app level
	es_client = search.es_connect()

	json_body = request.get_json()
	if json_body is None:
		# 400: Bad Request
		response = generic_helpers.set_endpoint_response(success=False, 
														 message='No request body was provided or the content type is not application/json',
														 status_code=400)
	if response['success']:
		func_mapping = {'basic_search': chart_utils.basic_search_charts,
						'similarity_search': chart_utils.similarity_search_charts,
						'advanced_search': chart_utils.advanced_search_charts}
	   	# If query type not present, return error
		query_type = json_body.get('query_type')
		if not query_type:
			# 400: Bad Request
			response = generic_helpers.set_endpoint_response(success=False, 
														 	 message='Paramater \'query_type\' must be provided',
														 	 status_code=400)
		elif query_type not in func_mapping:
			# 400: Bad Request
			response = generic_helpers.set_endpoint_response(success=False, 
														 	 message=f'Paramater \'query_type\' must be one of {list(func_mapping.keys())}',
														 	 status_code=400)
		else:
			func_response = func_mapping[query_type](es_client, json_body)
			
			if not func_response['success']:
				# 400: Bad Request
				response = generic_helpers.set_endpoint_response(success=False, message=func_response['message'],
																 status_code=400)
			else:
				response = generic_helpers.set_endpoint_response(success=True, 
																 results=func_response['chart_data'],
																 status_code=200)
	return jsonify(response), response['status_code']