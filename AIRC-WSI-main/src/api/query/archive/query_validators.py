# Generic helper functions
from ..generic_utils import generic_helpers
# Pattern matching
import re


################
# BASIC SEARCH #
################

def validate_query_text_param(query_text):
    response = generic_helpers.set_helper_response()

    if query_text is None:
        response = generic_helpers.set_helper_response(response,
                                                   success=False,
                                                   message='Parameter \'query_text\' must be provided')
    elif not validate_text(query_text):
        response = generic_helpers.set_helper_response(response,
                                                   success=False,
                                                   message='Parameter \'query_text\' must only contain alphanumeric characters, spaces, parenthesis, double quotes, asterisks, and tildas')
    if response['success']:
        # There is a space char expected around operators
        symbol_mappings = {" AND ": "+", " OR ": "|", " NOT ": "-", " AND NOT ": "+-"}
        # Replace word operators with symbol equivalents
        for op, sym in symbol_mappings.items():
            query_text = re.sub(op, sym, query_text)
    response['query_text'] = query_text
    return response

# This function returns True if string DOES NOT contain unexpected character, False if it does
def validate_text(text):
    text = str(text)
    # If string contains anything other than alphanumeric chars, spaces, 
    # double quotes, or parenthesis, asterisk, return False
    regex = '[^a-zA-Z\d\s\"\(\)\*]'
    return not re.compile(regex).search(text)

#####################
# SIMILARITY SEARCH #
#####################

# This function validates the paginate parameters for the vector_search function specifically
# The param should take two values, a float in position 0, and an int in position 1
'''
def validate_similarity_paginate_param(paginate_values):
    return_value = None
    # If list is empty, return None
    if paginate_values:
        # If first value can't be cast to float and second to int, values are not accepted
        try:

            paginate_values = [num for num in paginate_values.split(',')]
            value1 = float(paginate_values[0])
            value2 = int(paginate_values[1])
            return_value = [value1, value2]
        except ValueError:
            pass
    # Otherwise, return values
    return return_value
'''

def validate_similarity_include_exclude_param(include, exclude):
    response = generic_helpers.set_helper_response()
    # If include is not provided, do not validate
    if not include and not exclude:
        response = generic_helpers.set_helper_response(response,
                                                       success=False,
                                                       message='One of parameters \'attractors\' and \'repellers\' must be provided')
    if response['success']:
        # Check if include and exclude are of type list
        if not isinstance(include, list) or not isinstance(exclude, list):
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message='Parameters \'attractors\' and \'repellers\' must be of type Array or List')
    if response['success']:
        # Determine if values in include and exclude are alphanumeric characters (no special characters except space)
        # all() function returns True if all elements in a list are True, otherwise False
        # isalnum() returns True if all characters in a string are alphanumeric, otherwise False
        # Ex: ["the quick", "brown"," fox  ", "jumped "] -> ["the", "quick", "brown", "", "fox", "", "jumped", ""]
        # -> [True, True, True, False, True, False, True, False] -> False
        if include:
            include_is_alnum = all([str(word).isalnum() for phrase in include for word in phrase.split(' ') if word])
        else:
            include_is_alnum = False
        if exclude:
            exclude_is_alnum = all([str(word).isalnum() for phrase in exclude for word in phrase.split(' ') if word])
        else:
            exclude_is_alnum = False
        if not include_is_alnum and not exclude_is_alnum:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message='Parameters \'attractors\' and \'repellers\' must only contain\
                                                           alphanumeric characters and spaces')
    return response
