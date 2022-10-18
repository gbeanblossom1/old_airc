# Generic helper functions
from ..generic_utils import generic_helpers
# Import flask app context
from flask import current_app as app

######################
# PROCESSING HELPERS #
######################

# Gives a dictionary mapping from index name to the function that will process results from that index
def get_processing_functions():
    # Will add more processing functions as more data types are added
    func_mapping = {app.settings["ES_INDICES"]["PUBLICATIONS"] : process_publications, app.settings["ES_INDICES"]["PATENTS"]: process_patents,
                    app.settings["ES_INDICES"]["GRANTS"] : process_grants, app.settings["ES_INDICES"]["COMPANIES"] : process_companies}
    return func_mapping

######################### 
# ELASTICSEARCH HELPERS #
#########################

# Given a list of (valid) data types, this function maps those data types to their corresponding ElasticSearch index
def get_index_names_by_data_type(data_types):
    response = generic_helpers.set_helper_response()

    if data_types is None:
        response = generic_helpers.set_helper_response(response,
                                                       success=False,
                                                       message=f'Parameter \'data type\' is invalid. Must be one of \
                                                       {[dt for dt in index_mapping]}')
    if response['success']:
        index_list = list(app.settings["ES_INDICES"].values())
        for dt in data_types:
            if str(dt).lower() not in index_list:
                response = generic_helpers.set_helper_response(response,
                                                               success=False,
                                                               message=f'Parameter \'data type\' is invalid. Must be one of \
                                                               {index_list}')
                break
    # All provided data types are valid
    if response['success']:
        response['indices'] = [dt.lower() for dt in data_types]
    
    return response

# Send filters with params
def create_json_requests(indices, func, func_params, request_cache=False, shard_pref=None):
    json_request = []
    for index in indices:
        header = {"index": index, "request_cache": request_cache}
        if shard_pref:
            header['preference'] = shard_pref
        json_request.append(header)
        # Add index to params, as some functions require it
        func_params['index'] = index
        # Build query
        query = func(**func_params)
        json_request.append(query)
    return json_request

##########################
# DOCUMENT COUNT HELPERS #
##########################

# Given a label, this function returns that label's sort order
def sort_numbers(label):
    orderings = {"Total Documents": 0, 
                 "Total Publications": 1, 
                 "Scopus": 2, 
                 "arXiv": 3,
                 "Total Patents": 4, 
                 "Derwent World Patent Index": 5,
                 "Total Grants": 6,
                 "NSF": 7,
                 "NIH": 8,
                 "SBIR": 9,
                 "Total Companies": 10,
                 "Crunchbase": 11}
    return orderings[label]


#######################
# PUBLICATION HELPERS #
#######################

# Given a set of results from the publications index, process and return
# WILL NEED TO CHANGE AS DATA IS INCORPORATED INTO ELASTICSEARCH
def process_publications(res):

    return {
            "data_type": app.settings["ES_INDICES"]["PUBLICATIONS"],
            "total_hits": res['hits']['total']['value'],
            "filters": process_publication_filters(res['aggregations']),
            "records": [hit['_source'] for hit in res['hits']['hits']]
        }

def process_publication_filters(aggs):
    # If a sample was used to generate filters (ie. for vector search)
    # need to pull data from nested dict
    if "sample" in aggs:
        aggs = aggs["sample"]

    filter_names = {
        "data_src_filter": "Data Source", 
        "year_filter": "Year",
        "org_filter": "Organization", 
        "country_filter": "Country",
        "author_filter": "Author",
        "auth_kwds_filter": "Author Keywords",   
        "funding_agency_filter": "Funding Agency", 
        "subj_area_filter": "Classification", 
        "src_title_filter": "Source Title",
        "doc_type_filter": "Document Type"   
    }
    # Nested filters have two levels and must be treated differently
    nested_filter_names = {("conf_filter_nested", "conf_name_filter"): "Conference Name"}
    # Add non-nested filters
    #filters = {fname: aggs[fname]['buckets'] for fname in filter_names}
    filters = [{"filter_name": fname, "display_label": disp_label, "filter_data": aggs[fname]['buckets']} for fname, disp_label in filter_names.items()]
    # Add nested filters
    for fname_tuple, disp_label in nested_filter_names.items():
        #filters[f[1]] = aggs[f[0]][f[1]]['buckets']
        filters.append({"filter_name": fname_tuple[1], "display_label": disp_label, "filter_data": aggs[fname_tuple[0]][fname_tuple[1]]['buckets']})

    return filters

##################
# PATENT HELPERS #
##################

def process_patents(res):
    return {
            "data_type": app.settings["ES_INDICES"]["PATENTS"],
            "total_hits": res['hits']['total']['value'],
            "filters": process_patent_filters(res['aggregations']),
            "records": [hit['_source'] for hit in res['hits']['hits']]
        }
    '''
    # TEMPORARY UNTIL DATA_SOURCE_ID IS PRESENT IN DATA
    records = [hit['_source'] for hit in res['hits']['hits']]
    for r in records:
        if r['es_uid']:
            r['data_source_id'] = r['es_uid'].split('_')[-1]
        else:
            r['data_source_id'] = None
    '''
    #response['records'] = records
    #return response

def process_patent_filters(aggs):
    # If a sample was used to generate filters (ie. for vector search)
    # need to pull data from nested dict
    if "sample" in aggs:
        aggs = aggs["sample"]

    # Using dict to store names as they come from elasticsearch and a frontend display label
    filter_names = {
        "data_src_filter": "Data Source", 
        "year_filter": "Year",
        "inventor_filter": "Inventor", 
        "assignee_filter": "Assignee",
        "country_filter": "Country (Assignee)", 
        "patent_office_filter": "Patent Office", 
        "derwent_class_filter": "Derwent Classification", 
        "descriptor_filter": "Descriptor", 
    }
    # Add non-nested filters
    return [{"filter_name": fname, "display_label": disp_label, "filter_data": aggs[fname]['buckets']} for fname, disp_label in filter_names.items()]

#################
# GRANT HELPERS #
#################

def process_grants(res):
    return {
            "data_type": app.settings["ES_INDICES"]["GRANTS"],
            "total_hits": res['hits']['total']['value'],
            "filters": process_grant_filters(res['aggregations']),
            "records": [hit['_source'] for hit in res['hits']['hits']]
        }

def process_grant_filters(aggs):
    # If a sample was used to generate filters (ie. for vector search)
    # need to pull data from nested dict
    if "sample" in aggs:
        aggs = aggs["sample"]

    filter_names = {
        "data_src_filter": "Data Source",
        "award_year_filter": "Award Year",
        "principal_inv_filter": "Principal Investigator",
        "institution_filter": "Institution",
        "state_filter": "State",
        "country_filter": "Country",
        "awarding_branch_filter": "Awarding Branch",
        "sbir_program_filter": "SBIR Program",
        "sbir_phase_filter": "SBIR Phase",
        "research_kwds_filter": "Research Keywords",
        "award_amount_range_filter": "Award Amount"
    }
    # Add all filters besides award amounts
    filters = [{"filter_name": fname, "display_label": disp_label, "filter_data": aggs[fname]['buckets']} 
             for fname, disp_label in filter_names.items()
             if fname != "award_amount_range_filter"]
    # Add award amounts (need to add separately to make sure they are sorted in the correct order)
    filters.append({
            "filter_name": "award_amount_range_filter",
            "display_label": filter_names["award_amount_range_filter"],
            "filter_data": sorted(aggs["award_amount_range_filter"]["buckets"],
                                  key=lambda x:app.settings["DATA_TYPE_OPTIONS"]["GRANTS"]["AWARD_RANGES"].index(x['key']))

        })
    return filters

###################
# COMPANY HELPERS #
###################

def process_companies(res):
    return {
            "data_type": app.settings["ES_INDICES"]["COMPANIES"],
            "total_hits": res['hits']['total']['value'],
            "filters": process_company_filters(res['aggregations']),
            "records": [hit['_source'] for hit in res['hits']['hits']]
        }

def process_company_filters(aggs):
    # If a sample was used to generate filters (ie. for vector search)
    # need to pull data from nested dict
    if "sample" in aggs:
        aggs = aggs["sample"]

    filter_names = {
        "data_src_filter": "Data Source",
        "year_filter": "Founded Year",
        "status_filter": "Status",
        "state_filter": "State/Province",
        "country_filter": "Country",
        "category_groups_filter": "Industry",
        "employee_count_filter": "Employee Count",
        "woman_owned_filter": "Woman Owned",
        "socec_disadvantaged_filter": "Socially/Economically Disadvantaged",
        "investor_funding_filter": "Investor Funding"
    }
    # Add all filters besides funding amounts
    filters = [{"filter_name": fname, "display_label": disp_label, "filter_data": aggs[fname]['buckets']} 
             for fname, disp_label in filter_names.items()
             if fname != "investor_funding_filter"]
    # Add funding amounts (need to add separately to make sure they are sorted in the correct order)
    filters.append({
            "filter_name": "investor_funding_filter",
            "display_label": filter_names["investor_funding_filter"],
            "filter_data": sorted(aggs["investor_funding_filter"]["buckets"],
                                  key=lambda x:app.settings["DATA_TYPE_OPTIONS"]["COMPANIES"]["FUNDING_RANGES"].index(x['key']))

        })
    return filters
