# Generic helper functions
from ..generic_utils import generic_helpers
# Import flask app context
from flask import current_app as app
import sys

def process_chart_results(results, index):
	func_switch = {
		app.settings['ES_INDICES']['PUBLICATIONS']: process_chart_results_publications,
		app.settings['ES_INDICES']['PATENTS']: process_chart_results_patents,
		app.settings['ES_INDICES']['GRANTS']: process_chart_results_grants,
		app.settings['ES_INDICES']['COMPANIES']: process_chart_results_companies
	}

	return func_switch[index](results, index)


################
# PUBLICATIONS #
################

def process_chart_results_publications(results, index):
	response = generic_helpers.set_helper_response()

	func_mapping = {
		"top_authors_composite": top_authors_composite_pubs,
		"top_authors_table": top_authors_table_pubs, 
		"count_by_year": count_by_year_pubs, 
		"count_by_year_by_doc_type": count_by_year_by_doc_type_pubs, 
		"top_funders_by_doc_count": top_funders_by_doc_count_pubs,
		#"top_funders_by_doc_count_fvey": top_funders_by_doc_count_fvey_pubs,
		"top_countries_by_doc_count": top_countries_by_doc_count_pubs,
		"word_cloud": word_cloud_pubs
	}

	# Check if using vector search
	if 'sample' in results:
		results = results['sample']
		del results["doc_count"]
	# top_authors_table needs special processing since it is a nested aggregation
	response["chart_data"] = [ {"chart_name": chart_name,
								"chart_data": func_mapping[chart_name](results[chart_name]["buckets"])} 
							  for chart_name in results
							  if chart_name != "top_authors_table" 
							  and chart_name != "top_funders_by_doc_count_fvey"
							  and chart_name != "top_funders_by_doc_count_dod"]
	
	if "top_authors_table" in results:
		response["chart_data"].append({"chart_name": "top_authors_table", "chart_data": top_authors_table_pubs(results["top_authors_table"]["top_authors_nested"]["buckets"])})

	# Extra processing step to handle special case for filtered aggregations
	for chart in ["top_funders_by_doc_count_fvey", "top_funders_by_doc_count_dod"]:
		if chart in results:
			response["chart_data"].append({"chart_name": chart, 
									   "chart_data": top_funders_by_doc_count_pubs(results[chart]["top_funders"]["buckets"])})

	return response

def top_authors_composite_pubs(buckets):
	if not buckets:
		return None
	else:
		return [{"name": item["key"], 
				 "doc_count": item["doc_count"],
				 "num_cites": int(item["num_cites"]["value"]), 
				 "composite_score": int(item["doc_count"] * item["num_cites"]["value"])}
				 for item in buckets]

def top_authors_table_pubs(buckets):
	if not buckets:
		return None
	else:
		results = []
		count = 1
		for item in buckets:
			doc_count = item["doc_count"]
			source = item["top_hits_agg"]["hits"]["hits"][0]["_source"]

			affs = source.get("affiliations")
			if affs:
				aff_list = [item.get("aff_parent_name") 
							for item in affs
							if item.get("aff_parent_name")]
				country_list = [item.get("aff_country") 
							for item in affs
							if item.get("aff_country")]
				aff = ', '.join(aff_list)
				country = ', '.join(country_list)
			else:
				aff = None
				country = None

			author = source.get("auth_fullname")

			cites = int(item["num_cites"]["num_cites_nested"]["value"])
			composite_score = int(item["composite_score_script"]["value"])

			results.append({"doc_count": doc_count,
							"num_cites": cites,
							"composite_score": composite_score, 
							"author": author, 
							"affiliation": aff, 
							"country": country, 
							"rank": count})
		return results

def count_by_year_pubs(buckets):
	if not buckets:
		return None
	else:
		return [{"year": item["key"], "count": item["doc_count"]} for item in buckets]

def count_by_year_by_doc_type_pubs(buckets):
	if not buckets:
		return None
	else:
		return [{"year": item["key"]["year"], 
				 "doc_type": item["key"]["doc_type"],
				 "doc_count": item["doc_count"]}
				 for item in buckets]

def top_funders_by_doc_count_pubs(buckets):
	if not buckets:
		return None
	else:
		return [{"name": item["key"], "count": item["doc_count"]} for item in buckets]

def top_countries_by_doc_count_pubs(buckets):
	if not buckets:
		return None
	else:
		return [{"name": item["key"], "count": item["doc_count"]} for item in buckets]

def word_cloud_pubs(buckets):
	if not buckets:
		return None
	else:
		return word_cloud(buckets)

###########
# PATENTS #
###########

def process_chart_results_patents(results, index):
	response = generic_helpers.set_helper_response()

	func_mapping = {
		"top_inventors_table": top_inventors_table_patents,
		"count_by_year": count_by_year_patents,
		"top_assignees_by_doc_count": top_assignees_by_doc_count_patents,
		"top_countries_by_doc_count": top_countries_by_doc_count_patents,
		"word_cloud": word_cloud_patents
	}

	# Check if using vector search
	if 'sample' in results:
		results = results['sample']
		del results["doc_count"]
	# top_authors_table needs special processing since it is a nested aggregation
	response["chart_data"] = [ {"chart_name": chart_name,
								"chart_data": func_mapping[chart_name](results[chart_name]["buckets"])} 
							  for chart_name in results
							  if chart_name != "top_inventors_table"]
	
	if "top_inventors_table" in results:
		response["chart_data"].append({"chart_name": "top_inventors_table", "chart_data": top_inventors_table_patents(results["top_inventors_table"]["nested_agg"]["buckets"])})

	return response

def count_by_year_patents(buckets):
	if not buckets:
		return None
	else:
		return [{"year": item["key"], "count": item["doc_count"]} for item in buckets]

def top_assignees_by_doc_count_patents(buckets):
	if not buckets:
		return None
	else:
		return [{"name": item["key"], "count": item["doc_count"]} for item in buckets]

def top_countries_by_doc_count_patents(buckets):
	if not buckets:
		return None
	else:
		return [{"name": item["key"], "count": item["doc_count"]} for item in buckets]

def word_cloud_patents(buckets):
	if not buckets:
		return None
	else:
		return word_cloud(buckets)

def top_inventors_table_patents(buckets):
	if not buckets:
		return None
	else:
		results = []
		count = 1
		for item in buckets:
			name = item["key"]
			# Get doc count
			doc_count = item["doc_count"]
			# Get pi object/data
			source = item["top_hits_agg"]["top_hits_agg_nested"]["hits"]["hits"][0]["_source"]
			countries = source.get("assignee_countries")
			if countries is not None:
				countries = ', '.join(countries)
			else:
				countries = None

			assignees = source.get("assignee_list")
			if assignees is not None:
				assignees = ', '.join(assignees)
			else:
				assignees = None

			results.append({"doc_count": doc_count, "inventor": name, "assignees": assignees, "countries": countries, "rank": count})
			count +=1
		return results

##########
# GRANTS #
##########

def process_chart_results_grants(results, index):
	response = generic_helpers.set_helper_response()

	func_mapping = {
		'count_by_year_by_source': count_by_year_by_source_grants,
		'top_institutions_by_count_by_source': top_institutions_by_count_by_source_grants,
		'top_principal_investigator_table': top_principal_investigator_table_grants,
		'top_funders_by_doc_count': top_funders_by_doc_count_grants,
		#'top_funders_by_doc_count_fvey': top_funders_by_doc_count_fvey_grants,
		#'top_funders_by_doc_count_dod': top_funders_by_doc_count_dod_grants,
		'word_cloud': word_cloud_grants
	}
	
	# Check if using vector search
	if "sample" in results:
		results = results["sample"]
		del results["doc_count"]
	# top_authors_table needs special processing since it is a nested aggregation
	response["chart_data"] = [ {"chart_name": chart_name,
								"chart_data": func_mapping[chart_name](results[chart_name]["buckets"])} 
							  for chart_name in results
							  if chart_name != "top_principal_investigator_table" 
							  and chart_name != "top_funders_by_doc_count_fvey"
							  and chart_name != "top_funders_by_doc_count_dod"]
	
	# Extra processing step to handle special case for PI table
	if "top_principal_investigator_table" in results:
		response["chart_data"].append({"chart_name": "top_principal_investigator_table", 
									   "chart_data": top_principal_investigator_table_grants(results["top_principal_investigator_table"]["nested_agg"]["buckets"])})
	# Extra processing step to handle special case for filtered aggregations
	for chart in ["top_funders_by_doc_count_fvey", "top_funders_by_doc_count_dod"]:
		if chart in results:
			response["chart_data"].append({"chart_name": chart, 
									   "chart_data": top_funders_by_doc_count_grants(results[chart]["top_funders"]["buckets"])})
	return response

def count_by_year_by_source_grants(buckets):
	if not buckets:
		return None
	else:
		return [{"year": item["key"]["year"], 
				 "source": item["key"]["source"],
				 "doc_count": item["doc_count"]}
				 for item in buckets]

def top_institutions_by_count_by_source_grants(buckets):
	if not buckets:
		return None
	else:
		return [{'organization': item['key'], 'doc_count': item['doc_count']} for item in buckets]
		''' 
		return [{"organization": item["key"]["org"], 
				 "source": item["key"]["source"],
				 "doc_count": item["doc_count"]}
				 for item in buckets]
		'''

def top_principal_investigator_table_grants(buckets):
	if not buckets:
		return None
	else:
		##################################################
		results = []
		count = 1
		for item in buckets:
			name = item["key"]
			# Get doc count
			doc_count = item["doc_count"]
			# Get pi object/data
			source = item["top_hits_agg"]["top_hits_agg_nested"]["hits"]["hits"][0]["_source"]
			pi_list = source.get("investigators")

			for pi in pi_list:
				if name == pi.get("inv_full_name"):
					orgs = pi.get("inv_aff")
					if orgs:
						orgs = orgs[0]
					else:
						orgs = None
					countries = source.get('countries')
					if countries:
						countries = countries[0]
					break
			results.append({"doc_count": doc_count, "pi": name, "org": orgs, "country": countries, "rank": count})
			count +=1 
		return results

def top_funders_by_doc_count_grants(buckets):
	if not buckets:
		return None
	else:
		return [{'name': item['key'], 'doc_count': item['doc_count']} for item in buckets]

def word_cloud_grants(buckets):
	if not buckets:
		return None
	else:
		return word_cloud(buckets)

#############
# COMPANIES #
#############

def process_chart_results_companies(results, index):
	response = generic_helpers.set_helper_response()

	func_mapping = {
		'count_by_org_size': count_by_org_size_companies,
		'top_companies_by_funding_table': top_companies_by_funding_table_companies,
		'top_countries_by_org_count': top_countries_by_org_count_companies,
		'word_cloud': word_cloud_companies
	}

	# Check if using vector search
	if 'sample' in results:
		results = results['sample']
		del results["doc_count"]
	# top_companies_by_funding_table needs special processing since it is a hop_hits aggregation
	response["chart_data"] = [ {"chart_name": chart_name,
								"chart_data": func_mapping[chart_name](results[chart_name]["buckets"])} 
							  for chart_name in results
							  if chart_name != "top_companies_by_funding_table"]
	
	if "top_companies_by_funding_table" in results:
		response["chart_data"].append({"chart_name": "top_companies_by_funding_table", 
									   "chart_data": top_companies_by_funding_table_companies(results["top_companies_by_funding_table"]["hits"]["hits"])})

	return response

def count_by_org_size_companies(buckets):
	if not buckets:
		return None
	else:
		return [{"org_size": item["key"], "count": item["doc_count"]} for item in buckets]

# This function utilizes an ElasticSearch "top_hits" aggregation that returns records
# ranked by some value
def top_companies_by_funding_table_companies(hits):
	if not hits:
		return None
	else:
		return [{"org_name": item["_source"]["name"], "funding": item["_source"]["total_funding_usd"]}
				for item in hits]

def top_countries_by_org_count_companies(buckets):
	if not buckets:
		return None
	else:
		return [{"country": item["key"], "count": item["doc_count"]} for item in buckets]

def word_cloud_companies(buckets):
	if not buckets:
		return None
	else:
		return word_cloud(buckets)

############
# GENERICS #
############

def word_cloud(buckets):
	# Normalize doc counts to values between 0-1
	doc_counts = [item['doc_count'] for item in buckets]
	min_val = min(doc_counts)
	max_val = max(doc_counts)

	if not (max_val - min_val):
		return [{"term": item["key"], "count": 1} for item in buckets]
	else:
		return [{"term": item["key"], "count": round((item["doc_count"] - min_val)/(max_val - min_val), 3)} for item in buckets]