# Generic helper functions
from ..generic_utils import generic_helpers
# Import flask app context
from flask import current_app as app

def validate_chart_request(chart_list, data_type):
	response = generic_helpers.set_helper_response()

	if chart_list is None:
			# 400: Bad Request
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message='Parameter \'charts\' must be present')
	# If request is singleton, convert it to list for generalized for loop processing
	if not isinstance(chart_list, list):
		chart_list = [chart_list]

	if response['success']:
		chart_items = []
		for item in chart_list:
			func_response = validate_charts(item, data_type)
			if not func_response['success']:
				# 400: Bad Request
				response = generic_helpers.set_helper_response(response,
															   success=False, 
															   message=func_response['message'])
				break
			else:
				chart_items.append(func_response['item'])
		response['chart_items'] = chart_items
	return response

def validate_charts(item, data_type):
	response = generic_helpers.set_helper_response()

	name = item.get('chart_name')
	size = item.get('chart_size')
	order = item.get('order')
	# User submitted list of charts with missing chart_name
	if name is None:
		# 400: Bad Request
		response = generic_helpers.set_helper_response(response,
													   success=False, 
													   message='Parameter \'chart_name\' must be present for all requested charts')
	else:
		# This compares the chart name given by the user to the list of valid chart names
		# If it evaluates to false, name is invalid and api returns an error
		if name not in app.settings["CHARTS"][data_type.upper()]:
			# 400: Bad Request
			response = generic_helpers.set_helper_response(response,
														   success=False, 
														   message=f'Parameter \'chart_name\' must be one of {app.settings["CHARTS"][data_type.upper()]} for data type \'{data_type}\'')
	if response['success']:
		# If size is not provided, it is set to the max allowable size
		if size is None:
			size = app.settings["CHARTS"]["DEFAULT_CHART_SIZE"]
		else:
			try:
				size = int(size)
			except ValueError:
				# 400: Bad Request
				response = generic_helpers.set_helper_response(response,
															   success=False, 
														 	   message=f'Parameter \'chart_size\' must be an integer type')
			if response['success']:
				# Check that chart size is valid
				if size < 1 or size > app.settings["CHARTS"]["MAX_CHART_SIZE"]:
					# 400: Bad Request
					response = generic_helpers.set_helper_response(response,
																   success=False, 
																   message=f'Parameter \'chart_size\' must be between 1 and {app.settings["CHARTS"]["MAX_CHART_SIZE"]}')
	if response['success']:
		# If order is not provided, set it to the default order
		if order is None:
			order = app.settings["CHARTS"]["DEFAULT_ORDER"]
		else:
			# Otherwise, check if it is one of the valid options
			order = str(order)
			if order not in app.settings["CHARTS"]["ORDER_OPTIONS"]:
				# 400: Bad Request
				response = generic_helpers.set_helper_response(response,
															   success=False, 
															   message=f'Parameter \'order\' must be one of {app.settings["CHARTS"]["ORDER_OPTIONS"]}')
	# Adjust values of item
	item['chart_size'] = size
	item['order'] = order
	response['item'] = item
	return response