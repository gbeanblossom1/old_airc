import random
import re
import sys
# To validate inputs
from . import query_validators as validators
from ..generic_utils import generic_validators
# Query helper functions
from . import query_helpers as helpers
# Generic helper functions
from ..generic_utils import generic_helpers
# Sample data for tests
#from ..sample_data import samples
# Model helpers
import models
# To access ElasticSearch and Error handling
from elastipy import search, queryBuilder, exceptions
# import elastipy.exceptions
# Import flask app context
from flask import current_app as app



##################
# DOCUMENT COUNT #
##################

def doc_count_build_query():
    response = generic_helpers.set_helper_response()
    # Indices
    indices = list(app.settings['ES_INDICES'].values())

    # Specific parameters for query building function
    query_func_params = {'field_name': 'data_source.kw'}
    # Create json requests for ElasticSearch
    json_requests = helpers.create_json_requests(indices=indices,
                                                 func=queryBuilder.create_agg_query_terms,
                                                 func_params=query_func_params,
                                                 request_cache=False,
                                                 shard_pref='basic_search')
    response['json_requests'] = json_requests
    return response

def doc_count_get_counts(es_client, json_requests):
    response = generic_helpers.set_helper_response()
    try:
        response['results'] = search.document_count(es_client, json_requests)
    except exceptions.DatabaseConnectionError as e:
        response = generic_helpers.set_helper_response(response, success=False, message=e.message)
    except exceptions.ElastipyError as e:
        response = generic_helpers.set_helper_response(response, success=False, message=e.message)
    return response

def doc_count_process_results(results):
    response = generic_helpers.set_helper_response()
    doc_counts = []
    # 'Total' keeps track of the total number of documents across all indices
    total = 0
    # Mapping from index name to desired label name
    # May be put in a "global variables" file later
    label_mapping = {app.settings["ES_INDICES"]["PUBLICATIONS"]: "Total Publications", 
                     app.settings["ES_INDICES"]["PATENTS"]: "Total Patents", 
                     app.settings["ES_INDICES"]["GRANTS"]: "Total Grants", 
                     app.settings["ES_INDICES"]["COMPANIES"]: "Total Companies"}
                     
    for res in results:
        # 'Tally' keeps track of the total number of documents for a particular document type
        tally = 0
        # The document type is the only key in the response object, so collect it here
        document_type = list(res.keys())[0]

        # Access the buckets which contain the Source/Document Count pairs
        buckets = res[document_type]["buckets"]
        # For each bucket, append Source/Document Count pairs to 'doc_counts' list
        for b in buckets:
            doc_counts.append({"label": b["key"],
                               "key": re.sub(" ", "_", b["key"].lower()),
                               "value": b["doc_count"],
                               "sort": helpers.sort_numbers(b["key"])})
            # Track tally for this Source
            tally += b["doc_count"]
        # Add total document counts for each document type
        doc_counts.append({"label": label_mapping[document_type],
                           "key": re.sub(" ", "_", label_mapping[document_type].lower()),
                           "value": tally,
                           "sort": helpers.sort_numbers(label_mapping[document_type])})
        total += tally
    # Add total document counts
    doc_counts.append({"label": "Total Documents",
                       "key": "total_documents",
                       "value": total,
                       "sort": helpers.sort_numbers("Total Documents")})

    sorted_doc_counts = sorted(doc_counts, key=lambda doc: doc['sort'])
    # Remove sort field
    for doc in sorted_doc_counts:
        del doc['sort']
    response['doc_counts'] = sorted_doc_counts
    return response
    
################
# BASIC SEARCH #
################

def basic_search_validate(req_params, input_params, data_types, category, query_text,
                          start_year, end_year, page_size, page_number, filters):
    response = generic_helpers.set_helper_response()
    parameters = {}
    # Collect input param keys as list and check if required params are present
    func_response = generic_validators.check_valid_params(req_params, input_params)
    if not func_response['success']:
        response = generic_helpers.set_helper_response(response,
                                                       success=False,
                                                       message=func_response['message'])
    # Checks if data types provided are valid
    # indices will be a list of ElasticSearch indices to search
    if response['success']:
        func_response = helpers.get_index_names_by_data_type(data_types)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['indices'] = func_response['indices']
    # Checks if category type provided is valid
    if response['success']:
        func_response = generic_validators.validate_category_param(category)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['category'] = func_response['category']

    # Checks if query_text is valid
    if response['success']:
        func_response = validators.validate_query_text_param(query_text)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['query_text'] = func_response['query_text']

    # Check start and end year parameters
    if response['success']:
        func_response = generic_validators.validate_year_params(start_year, end_year)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['start_year'] = func_response['start_year']
            parameters['end_year'] = func_response['end_year']

    # Checks page_size param
    if response['success']:
        func_response = generic_validators.validate_page_size_param(page_size)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['page_size'] = func_response['page_size']

    # Checks if page_number param is valid
    if response['success']:
        func_response = generic_validators.validate_page_num_param(page_number)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['page_number'] = func_response['page_number']

    # VALIDATE FILTERS
    if response['success']:
        # MAKE SURE THAT ALL DATA TYPES GIVEN IN FILTERS ARE ALSO GIVEN IN DATA_TYPES PARAM
        if filters:
            # If filters object is not a list, convert it into one
            if not isinstance(filters, list):
                filters = [filters]
            # Reformats input filters to nicer format for ElasticSearch
            try:
                parameters['filters'] = {f['data_type']: {
                                            'restrict_to': {item["filter_key"]: item["filter_values"] for item in f['restrict_to']}, 
                                            'exclude': {item["filter_key"]: item["filter_values"] for item in f['exclude']}}
                                        for f in filters}
            # For each given data type, , and should always
            # be a list
            except KeyError:
                response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=('Parameter \'filters\' is malformed. For each data type, parameters' 
                                                           ' \'restrict_to\' and \'exclude\' must be provided, and each should always be a list'))
        else:
            parameters['filters'] = None


    response['parameters'] = parameters
    return response

def basic_search_build_query(es_client, indices, query_text, category, start_year, end_year, filters, page_size, page_number):
    response = generic_helpers.set_helper_response()
    # Specific parameters for query building function
    query_func_params = {'search_type': 'basic', 'query_text': query_text, 'category': category, 'start_year': start_year, 'end_year': end_year,
                         'filters': filters, 'from_size': page_number*page_size, 'to_size': page_size}
    # Create json requests for ElasticSearch
    json_requests = helpers.create_json_requests(indices=indices,
                                                 func=queryBuilder.create_basic_query,
                                                 func_params=query_func_params,
                                                 request_cache=True,
                                                 shard_pref='basic_search')

    # Validate query, need to create basic version of query without optional params to validate
    #query_func_params['sanitize'] = True
    #query_func_params['index'] = None
    #query_to_validate = queryBuilder.create_basic_query(**query_func_params)
    response['json_requests'] = json_requests
    return response

def basic_search_query_database(es_client, json_requests):
    response = generic_helpers.set_helper_response()
    # Error handling here, catch potential Elastipy errors
    try:
        # Run query to documents based on vectors
        response['results'] = search.basic_search(es_client, json_requests)['responses']
        #['responses']
    except exceptions.DatabaseConnectionError as e:
        response = generic_helpers.set_helper_response(response, success=False, message=e.message)
    except exceptions.ElastipyError as e:
        response = generic_helpers.set_helper_response(response, success=False, message=e.message)
    return response

def basic_search_process_results(results):
    #print(results)
    response = generic_helpers.set_helper_response()
    process_functions = helpers.get_processing_functions()
    # This results dictionary will hold results for each index
    documents = []
    # Will tally the document count across all data types
    total_doc_count = 0
    for r in results:
        # If there are no records from this index, move on to next index
        if not r['hits']['hits']:
            continue
        # Get index name from hits list (only place to get it)
        index_name = r['hits']['hits'][0]['_index']
        total_doc_count += r['hits']['total']['value']
        documents.append(process_functions[index_name](r))

    #response['documents'] = documents
    # Ensure that data types are always returned in the same order ()
    response['documents'] = [docs for index in list(app.settings["ES_INDICES"].values()) for docs in documents if docs["data_type"] == index]
    response['total_doc_count'] = total_doc_count
    return response

def basic_search_autocp(es_client, json_body):
    response = generic_helpers.set_helper_response()

    # Set es_client variable in app level
    es_client = search.es_connect(host=app.settings['ES_HOST'], port=app.settings['ES_PORT'])

    ##############
    # VALIDATION #
    ##############
    # Check if query body is present
    query_body = json_body.get('query')
    # If user does not want to put query parameters in a "query" field
    # they do not have to, the entire json body will be assumed to contain query params
    if not query_body:
        query_body = json_body

    # Check if autocp_size is present, if not, set to default 10
    autocp_size = json_body.get('autocp_size')
    if autocp_size is None:
        autocp_size = app.settings["AUTOCOMPLETE_OPTIONS"]["DEFAULT_SIZE"]
    else:
        try:
            autocp_size = int(autocp_size)
        except:
            # 400: Bad Request
            response = generic_helpers.set_helper_response(response,
                                                           success=False, 
                                                           message='Parameter \'autocp_size\' must be an integer type')

    autocp_text = json_body.get('autocp_text')
    autocp_field = json_body.get('autocp_field')
    if not autocp_text or not autocp_field:
        # 400: Bad Request
        response = generic_helpers.set_helper_response(response,
                                                       success=False, 
                                                       message='Parameters \'autocp_text\' and \'autocp_field\' must be present')
    if response['success']:
        # Required params
        req_params = ['data_types', 'category', "query_text", "start_year", "end_year"]
        func_response = basic_search_validate(req_params=req_params,
                                                    input_params=list(json_body.keys()),
                                                    data_types=json_body.get('data_types'),
                                                    category=json_body.get('category'),
                                                    query_text=json_body.get('query_text'),
                                                    start_year=json_body.get('start_year'),
                                                    end_year=json_body.get('end_year'),
                                                    page_size=0,
                                                    page_number=0,
                                                    filters=json_body.get('filters'))

        if not func_response['success']:
            # 400: Bad Request
            response = generic_helpers.set_helper_response(response, success=False, message=func_response['message'])
        else:
            parameters = func_response['parameters']

    ###############
    # BUILD QUERY #
    ###############
    if response['success']:
        func_response = basic_search_build_query(es_client, parameters['indices'], parameters['query_text'],
                                                       parameters['category'], parameters['start_year'],
                                                       parameters['end_year'], parameters['filters'], parameters['page_size'], 
                                                       parameters['page_number'])
        if not func_response['success']:
            # 400: Bad Request
            response = generic_helpers.set_helper_response(response, success=False, message=func_response['message'])
        else:
            json_requests = func_response['json_requests']

    # Add in autocomplete query
    if response['success']:
        for req in json_requests:
            # Either a header...
            if 'index' in req:
                index = req['index']
                continue
            # or a query
            else:
                # Specify required query for autocp results
                query, agg = queryBuilder.basic_search_autocp(index, autocp_text, autocp_field, autocp_size)
                if query is None or agg is None:
                    # 400: Bad Request
                    response = generic_helpers.set_helper_response(response, 
                                                                   success=False, 
                                                                   message='Parameter \'autocp_field\' is invalid')
                else:
                    req['query']['bool']['must'].append(query)
                # Add other part of query is request is still valid
                if response['success']:
                    # Specify required aggregation for autocp results
                    req['aggs'] = agg

    ##########
    # SEARCH #
    ##########

    if response['success']:
        func_response = basic_search_query_database(es_client, json_requests)

        if not func_response['success']:
            # 500: Internal Server Error
            response = generic_helpers.set_helper_response(response, success=False, message=func_response['message'])
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
        response['autocp_results'] = [item['key'] for item in
                                  func_response['results'][0]['aggregations']['autocp_suggestion']['autocp']['buckets']]

    return response

#################
# VECTOR SEARCH #
#################

def vector_search_validate(req_params, input_params, data_types, include, exclude, central_terms,
                           n_neighbors, start_year, end_year, page_size, page_number, filters):
    response = generic_helpers.set_helper_response()
    parameters = {}
    # Collect input param keys as list and check if required params are present
    func_response = generic_validators.check_valid_params(req_params, input_params)
    if not func_response['success']:
        response = generic_helpers.set_helper_response(response,
                                                       success=False,
                                                       message=func_response['message'])
    # Checks if data types provided are valid
    # indices will be a list of ElasticSearch indices to search
    if response['success']:
        func_response = helpers.get_index_names_by_data_type(data_types)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['indices'] = func_response['indices']

    # Checks if include,exclude is valid
    if response['success']:
        func_response = validators.validate_similarity_include_exclude_param(include, exclude)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['include'] = include
            parameters['exclude'] = exclude

    # Check start and end year parameters
    if response['success']:
        func_response = generic_validators.validate_year_params(start_year, end_year)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['start_year'] = func_response['start_year']
            parameters['end_year'] = func_response['end_year']

    # Checks page_size param
    if response['success']:
        func_response = generic_validators.validate_page_size_param(page_size)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['page_size'] = func_response['page_size']

    # Checks if page_number param is valid
    if response['success']:
        func_response = generic_validators.validate_page_num_param(page_number)
        if not func_response['success']:
            response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=func_response['message'])
        else:
            parameters['page_number'] = func_response['page_number']

    # VALIDATE FILTERS
    if response['success']:
        # MAKE SURE THAT ALL DATA TYPES GIVEN IN FILTERS ARE ALSO GIVEN IN DATA_TYPES PARAM
        if filters:
            # If filters object is not a list, convert it into one
            if not isinstance(filters, list):
                filters = [filters]
            # Reformats input filters to nicer format for ElasticSearch
            try:
                parameters['filters'] = {f['data_type']: {
                                            'restrict_to': {item["filter_key"]: item["filter_values"] for item in f['restrict_to']}, 
                                            'exclude': {item["filter_key"]: item["filter_values"] for item in f['exclude']}}
                                        for f in filters}
            # For each given data type, , and should always
            # be a list
            except KeyError:
                response = generic_helpers.set_helper_response(response,
                                                           success=False,
                                                           message=('Parameter \'filters\' is malformed. For each data type, parameters' 
                                                           ' \'restrict_to\' and \'exclude\' must be provided, and each should always be a list'))
        else:
            parameters['filters'] = None
    
    # ADD ADDITIONAL VALIDATION
    parameters['num_central_terms'] = int(central_terms)
    parameters['n_neighbors'] = int(n_neighbors)

    response['parameters'] = parameters
    return response

def vector_search_build_query(es_client, indices, include, exclude, n_neighbors,
                              page_size, page_number, start_year, end_year, filters):
    response = generic_helpers.set_helper_response()
    # Convert include & exclude to n-dimensional vector
    vector = models.get_search_vector(app.model, include, exclude)
    #vector = [random.uniform(-2, 2) for i in range(600)]
    # Need to figure out where to put fields to return
    #fields_to_return = []
    query_func_params = {'search_type': 'vector', 'vector': vector, 'vector_field_name': 'docvec', 'start_year': start_year, 'end_year': end_year,
                         'from_size': page_number*page_size, 'to_size': page_size, "n_neighbors": n_neighbors, "filters": filters}
    json_requests = helpers.create_json_requests(indices=indices,
                                                 func=queryBuilder.create_vector_query,
                                                 func_params=query_func_params,
                                                 request_cache=True,
                                                 shard_pref='vector_search')
    response['json_requests'] = json_requests
    return response

def vector_search_query_database(es_client, json_requests):
    response = generic_helpers.set_helper_response()
    # Error handling here, catch potential Elastipy errors
    try:
        # Run query to documents based on vectors
        response['results'] = search.vector_search(es_client, json_requests)['responses']
    except exceptions.DatabaseConnectionError as e:
        response = generic_helpers.set_helper_response(response, success=False, message=e.message)
    except exceptions.ElastipyError as e:
        response = generic_helpers.set_helper_response(response, success=False, message=e.message)
    return response

def vector_search_process_results(results, n_neighbors, num_central_terms):
    response = generic_helpers.set_helper_response()
    process_functions = helpers.get_processing_functions()
    # This results dictionary will hold results for each index
    documents = []
    # List for central terms
    terms = []
    # List for document scores
    scores = []
    for r in results:
        # If there are no records from this index, move on to next index
        if not r['hits']['hits']:
            continue

        # Get central terms
        terms.extend([hit['_source']['docvec_keywords'] for hit in r['hits']['hits']])
        # Get scores
        scores.extend([hit['_score'] - 1 for hit in r['hits']['hits']])
        # Get index name from hits list (only place to get it)
        index_name = r['hits']['hits'][0]['_index']
        #total_doc_count += r['hits']['total']['value']
        documents.append(process_functions[index_name](r))

    #response['documents'] = documents
    # Ensure that data types are always returned in the same order ()
    response['documents'] = [docs for index in list(app.settings["ES_INDICES"].values()) for docs in documents if docs["data_type"] == index]
    # Edit total document counts to reflect number of requested nearest neighbors
    for docs in response['documents']:
        docs['total_hits'] = n_neighbors
        for record in docs['records']:
            del record['docvec_keywords']

    response['total_doc_count'] = n_neighbors * len(documents)
    response['central_terms'] = models.get_central_terms(terms, scores, num_central_terms)
    return response

def similarity_search_autocp(es_client, json_body):
    pass

###################
# ADVANCED SEARCH #
###################

def advanced_search_autocp(es_client, json_body):
    pass