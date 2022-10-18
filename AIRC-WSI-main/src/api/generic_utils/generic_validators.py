from flask import current_app as app
# Generic helper functions
from . import generic_helpers
# Numpy
import numpy as np
# Datetime
import datetime

###########
# GENERAL #
###########

# Given list of required params and input params, determine if all required params are present
def check_valid_params(req_params, input_params):
	response = generic_helpers.set_helper_response()
	# Check if all required params are found in list of input params
	# Mask is a list of boolean values to determine which values in the list are correct
	mask = [elem in input_params for elem in req_params]
	if not all(mask):
		req_params = np.array(req_params)
		not_provided = req_params[np.invert(mask)].tolist()
		response = generic_helpers.set_helper_response(response,
													   success=False,
													   message=f'All required parameters are not present. Missing {not_provided}')
	return response

# Created a separate function to validate size param as this will be used across multiple search endpoints
def validate_page_size_param(page_size):
	response = generic_helpers.set_helper_response()
	if page_size is None:
		response = generic_helpers.set_helper_response(response,
													   success=False,
													   message='Required parameter page_size must be provided')
	if response['success']:
		# If value can't be cast to int, error
		try:
			size = int(page_size)
		except ValueError:
			response = generic_helpers.set_helper_response(response,
														   success=False,
														   message='Parameter page_size must be an integer')
	if response['success']:
		# If size is out of valid range, error
		if size < 0 or size > app.settings['MAX_PAGE_SIZE']:
			response = generic_helpers.set_helper_response(response,
														   success=False,
														   message=f'Parameter \'page_size\' must be between 1 and {app.settings["MAX_PAGE_SIZE"]}')
	response['page_size'] = size
	return response

def validate_page_num_param(page_num):
	response = generic_helpers.set_helper_response()
	# If page number is not provided, set to first page (0-indexing)
	if not page_num:
		page_num = 0

	# If value can't be cast to int, error
	try:
		page_num = int(page_num)
	except ValueError:
		response = generic_helpers.set_helper_response(response,
													   success=False,
													   message='Parameter page_num must be an integer')
	if response['success']:
		if page_num < 0:
			response = generic_helpers.set_helper_response(response,
													   success=False,
													   message='Parameter page_num must be a non-negative integer')
	response['page_number'] = page_num
	return response

def validate_category_param(cat):
	categories = ['Documents', 'People', 'Institutions']
	response = generic_helpers.set_helper_response()

	if cat not in categories:
		response = generic_helpers.set_helper_response(response,
													   success=False,
													   message=f'Provided category is invalid. Must be one of {categories}')
	else:
		response['category'] = cat
	return response

def validate_year_params(start, end):
	MIN_YEAR = 1600
	MAX_YEAR = datetime.datetime.now().year
	response = generic_helpers.set_helper_response()
	# Attempt to cast to int, if not, return error
	try:
		start = int(start)
		end = int(end)
	except ValueError:
		response = generic_helpers.set_helper_response(response,
													   success=False,
													   message='Parameters start_year and end_year must be integers')
	except TypeError:
		response = generic_helpers.set_helper_response(response,
													   success=False,
													   message='Parameters start_year and end_year must be provided')
	# They have successfully been cast to int
	if response['success']:
		# If the starting year is higher than ending year, return error
		if start > end:
			response = generic_helpers.set_helper_response(response,
														   success=False,
														   message='Parameter start_year must not be greater than parameter end_year')
		elif not MIN_YEAR <= start <= MAX_YEAR or not MIN_YEAR <= end <= MAX_YEAR:
			response = generic_helpers.set_helper_response(response,
														   success=False,
														   message=f'Parameters start_year and end_year must be between {MIN_YEAR} and {MAX_YEAR}')
	response['start_year'] = start
	response['end_year'] = end
	return response



