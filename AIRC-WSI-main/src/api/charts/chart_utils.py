from flask import request
# Query util functions
from ..query import query_utils
# Query helper functions
from ..query import query_helpers
# To access ElasticSearch and Error handling
from elastipy import search, queryBuilder, exceptions
# Generic helper functions
from ..generic_utils import generic_helpers
# Validation functions for charts
from . import chart_validators
# Import helpers functions for charts
from . import chart_helpers
import sys
from flask import current_app as app


def basic_search_charts(es_client, json_body):
	response = generic_helpers.set_helper_response()
	##############
	# VALIDATION #
	##############
	# Check if query body is present
	query_body = json_body.get('query')
	# If user does not want to put query parameters in a "query" field
	# they do not have to, the entire json body will be assumed to contain query params
	if not query_body:
		query_body = json_body

	charts_body = json_body.get('charts')
	if not charts_body:
		# 400: Bad Request
		response = generic_helpers.set_helper_response(response,
												   	   success=False, 
												   	   message='Parameter \'charts\' must be present')
	if response['success']:
		# Required params
		req_params = ['data_types', 'category', "query_text", "start_year", "end_year"]
		# Add data type to list if not already one
		data_type = query_body.get('data_types')
		if not isinstance(data_type, list):
			data_type = [data_type]
		func_response = query_utils.basic_search_validate(req_params=req_params,
													input_params=list(query_body.keys()),
													data_types=data_type,
													category=query_body.get('category'),
													query_text=query_body.get('query_text'),
													start_year=query_body.get('start_year'),
													end_year=query_body.get('end_year'),
													page_size=0,
													page_number=0,
													filters=query_body.get('filters'))

		if not func_response['success']:
			# 400: Bad Request
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			parameters = func_response['parameters']
	# Validate requested charts
	if response['success']:
		func_response = chart_validators.validate_chart_request(charts_body, data_type[0].lower())

		if not func_response['success']:
			# 400: Bad Request
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			# Charts may have been transformed during validation from a singleton to a list
			# so need to preserve that transformation by returning that value here
			charts = func_response['chart_items']

	###############
	# BUILD QUERY #
	###############
	if response['success']:
		func_response = query_utils.basic_search_build_query(es_client, parameters['indices'], parameters['query_text'],
													   parameters['category'], parameters['start_year'],
													   parameters['end_year'], parameters['filters'], parameters['page_size'], 
													   parameters['page_number'])
		if not func_response['success']:
			# 400: Bad Request
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			json_requests = func_response['json_requests']

	
	# Add in requested aggregations
	if response['success']:
		for req in json_requests:
			# Either a header...
			if 'index' in req:
				index = req['index']
				continue
			# or a query
			else:
				# User should specify desired charts
				req['aggs'] = queryBuilder.basic_search_charts_aggregations(index, charts)

	##########
	# SEARCH #
	##########

	if response['success']:
		func_response = query_utils.basic_search_query_database(es_client, json_requests)

		if not func_response['success']:
			# 500: Internal Server Error
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			pass

	### FIX PROCESS RESULTS SECTION ###
	### CHECK IF VALIDATION CAN BE DONE WITH JSON REQUESTS LIST ###
	### TEST ENDPOINT FOR VARIETY OF PARAMETERS ###
	### FAKE VECTOR SEARCH INDEX LIST TO KEEP IT WORKING ###

	###################
	# PROCESS RESULTS #
	###################
	if response['success']:

		# There should only be one set of results due to only accepting one data type
		func_response = chart_helpers.process_chart_results(func_response['results'][0]['aggregations'], query_body.get('data_types')[0].lower())

		if not func_response['success']:
			# 500: Internal Server Error
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			# 200: Ok
			response['chart_data'] = func_response['chart_data']

	return response


def similarity_search_charts(es_client, json_body):
	response = generic_helpers.set_helper_response()
	##############
	# VALIDATION #
	##############
	# Check if query body is present
	query_body = json_body.get('query')
	# If user does not want to put query parameters in a "query" field
	# they do not have to, the entire json body will be assumed to contain query params
	if not query_body:
		query_body = json_body

	charts_body = json_body.get('charts')
	if not charts_body:
		# 400: Bad Request
		response = generic_helpers.set_helper_response(response,
												   	   success=False, 
												   	   message='Parameter \'charts\' must be present')
	if response['success']:
		# Required params
		req_params = ['data_types', "page_size", "attractors"]
		# Add data type to list if not already one
		data_type = query_body.get('data_types')
		n_neighbors = query_body.get('nearest_neighbors')
		if not isinstance(data_type, list):
			data_type = [data_type]
		func_response = query_utils.vector_search_validate(req_params=req_params,
                                                 input_params=list(query_body.keys()),
                                                 data_types=data_type,
                                                 include=query_body.get('attractors'),
                                                 exclude=query_body.get('repellers'),
                                                 central_terms=query_body.get('central_terms'),
                                                 n_neighbors=n_neighbors,
                                                 start_year=query_body.get('start_year'),
                                                 end_year=query_body.get('end_year'),
                                                 page_size=query_body.get('page_size'),
                                                 page_number=query_body.get('page_number'),
                                                 filters=query_body.get('filters'))

		if not func_response['success']:
			# 400: Bad Request
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			parameters = func_response['parameters']
	# Validate requested charts
	if response['success']:
		func_response = chart_validators.validate_chart_request(charts_body, data_type[0].lower())

		if not func_response['success']:
			# 400: Bad Request
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			# Charts may have been transformed during validation from a singleton to a list
			# so need to preserve that transformation by returning that value here
			charts = func_response['chart_items']

	###############
	# BUILD QUERY #
	###############

	if response['success']:
		func_response = query_utils.vector_search_build_query(es_client, parameters['indices'], parameters['include'], parameters['exclude'],
                                                        parameters['n_neighbors'], parameters['page_size'],parameters['page_number'], 
                                                        parameters['start_year'], parameters['end_year'], parameters['filters'])
		if not func_response['success']:
			# 400: Bad Request
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			json_requests = func_response['json_requests']

	
	# Add in requested aggregations
	if response['success']:
		for req in json_requests:
			# Either a header...
			if 'index' in req:
				index = req['index']
				continue
			# or a query
			else:
				# User should specify desired charts
				# Use basic search chart aggs function for now since they are the same across search types
				#req['aggs'] = {
				#	"sample": {
				#		"sampler": {"shard_size": int(n_neighbors/app.settings["SEARCH_OPTIONS"]["SHARD_COUNTS"][index.upper()])},
				#		"aggs": queryBuilder.basic_search_charts_aggregations(index, charts)
				#	}
				#}
				req['aggs'] = queryBuilder.basic_search_charts_aggregations(index, charts)
				

	##########
	# SEARCH #
	##########

	if response['success']:
		func_response = query_utils.vector_search_query_database(es_client, json_requests)

		if not func_response['success']:
			# 500: Internal Server Error
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			pass

	### FIX PROCESS RESULTS SECTION ###
	### CHECK IF VALIDATION CAN BE DONE WITH JSON REQUESTS LIST ###
	### TEST ENDPOINT FOR VARIETY OF PARAMETERS ###
	### FAKE VECTOR SEARCH INDEX LIST TO KEEP IT WORKING ###

	###################
	# PROCESS RESULTS #
	###################

	if response['success']:
		# There should only be one set of results due to only accepting one data type
		func_response = chart_helpers.process_chart_results(func_response['results'][0]['aggregations'], query_body.get('data_types')[0].lower())

		if not func_response['success']:
			# 500: Internal Server Error
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=func_response['message'])
		else:
			# 200: Ok
			response['chart_data'] = func_response['chart_data']

	return response

def advanced_search_charts():
	pass