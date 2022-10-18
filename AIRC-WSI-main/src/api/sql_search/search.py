    ###############
    # BUILD QUERY #
    ###############

    func_response = utils.doc_count_build_query(indices)
    if not func_response['success']:
        # 400: Bad Request
        response = generic_helpers.set_endpoint_response(success=False, message=func_response['message'],
                                                         status_code=400)
    else:
        json_requests = func_response['json_requests']


    ##########
    # SEARCH #
    ##########

    if response['success']:

        func_response = utils.doc_count_get_counts(con, json_requests)
        # Run query to fetch the total document counts
        if not func_response['success']:
            # 500: Internal Server Error
            response = generic_helpers.set_endpoint_response(success=False, message=func_response['message'],
                                                         status_code=500)
        else:
            results = func_response['results']
