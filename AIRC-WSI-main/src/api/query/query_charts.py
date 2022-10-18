from collections import Counter
from dateutil.parser import parse


def generate_charts(data):
    charts = []
    # Vendor charts
    charts.extend(get_vendor_charts(data))
    # Naics charts
    charts.extend(get_naics_charts(data))
    # Commercial chart
    charts.extend(get_commercial_charts(data))
    # Contracting agency chart
    charts.extend(get_contracting_agency_charts(data))
    # Darpa chart
    charts.extend(get_darpa_charts(data))
    return charts


def get_darpa_charts(data):
    darpa_data = Counter()
    for record in data:
        agency = record["contracting_agency_name"]
        if "defense advanced research" in agency.lower():
            try:
                year = parse(str(record["date_signed"])).year
                darpa_data[year] += record["dollars_obligated"]
            except:
                continue

    darpa_data = [{"year": k, "total_dollars_obligated": v} for k,v in darpa_data.items()]
    return [create_chart_bar(darpa_data, sort_by="year", num_records=100,
                            x_column="year", y_column="total_dollars_obligated",
                            chart_name="darpa_line", reverse=False)]


def get_contracting_agency_charts(data):
    agencies = {}
    for record in data:
        agency = record["contracting_agency_name"]
        if agency not in agencies:
            agencies[agency] = {"contracting_agency_name": agency,
                                "total_dollars_obligated": record["dollars_obligated"]}
        else:
            agencies[agency]["total_dollars_obligated"] += record["dollars_obligated"]
    agencies = [{"contracting_agency_name": v["contracting_agency_name"],
                   "total_dollars_obligated": v["total_dollars_obligated"]}
                  for _, v in agencies.items()]
    return [create_chart_bar(agencies, sort_by="total_dollars_obligated", num_records=5,
                            x_column="contracting_agency_name", y_column="total_dollars_obligated",
                            chart_name="obligated_bar")]


def get_commercial_charts(data):
    com = Counter()
    for record in data:
        com[record["commercial"]] += 1
    return [{"chart_name": "commercial_pie", "chart_data": [{"name": k, "count": v}
                                                           for k,v in com.items()]}]


def get_naics_charts(data):
    naics_data = {}
    for record in data:
        naics_desc = record["naics_description"]
        if naics_desc not in naics_data:
            naics_data[naics_desc] = {"naics_description": naics_desc,
                                      "total_dollars_obligated": record["dollars_obligated"],
                                      "piids": [record["piid"]]}
        else:
            naics_data[naics_desc]["total_dollars_obligated"] += record["dollars_obligated"]
            naics_data[naics_desc]["piids"].append(record["piid"])

    naics_data = [{"naics_description": naics_desc,
                    "num_piids": len(set(v["piids"])),
                    "total_dollars_obligated": v["total_dollars_obligated"]}
                    for _, v in naics_data.items()]
    naics_charts = [create_chart_table(naics_data, sort_by="num_piids", num_records=100, chart_name="naics_table"),
                    create_chart_bar(naics_data, sort_by="num_piids", num_records=100, chart_name="naics_bar",
                                     x_column="naics_description", y_column="num_piids")]
    return naics_charts


def get_vendor_charts(data):
    vendor_data = {}
    for record in data:
        vendor_id = record["vendor_sam_entity_id"]
        if vendor_id not in vendor_data:
            vendor_data[vendor_id] = {"vendor_sam_entity_id": vendor_id,
                                     "vendor_name": record["vendor_name"],
                                     "total_dollars_obligated": record["dollars_obligated"],
                                     "piids": [record["piid"]]}
        else:
            vendor_data[vendor_id]["total_dollars_obligated"] += record["dollars_obligated"]
            vendor_data[vendor_id]["piids"].append(record["piid"])

    vendor_data = [{"vendor_sam_entity_id": v["vendor_sam_entity_id"],
                   "num_piids": len(set(v["piids"])),
                   "vendor_name": v["vendor_name"],
                   "total_dollars_obligated": v["total_dollars_obligated"]}
                  for _, v in vendor_data.items()]

    vendor_charts = [create_chart_table(vendor_data, sort_by="num_piids", num_records=100, chart_name="vendor_table"),
                     create_chart_bar(vendor_data, sort_by="num_piids", num_records=100, chart_name="vendor_bar",
                                      x_column="vendor_name", y_column="num_piids")]
    return vendor_charts


def create_chart_table(chart_data, sort_by, num_records, chart_name, reverse=True):
    chart_data = sorted(chart_data, reverse=reverse, key=lambda x: x[sort_by])[:num_records]
    return {"chart_name": chart_name, "chart_data": chart_data}


def create_chart_bar(chart_data, sort_by, num_records, x_column, y_column, chart_name, reverse=True):
    chart_data = sorted(chart_data, reverse=reverse, key=lambda x: x[sort_by])[:num_records]
    x_values = []
    y_values = []
    for i in chart_data:
        x_values.append(i[x_column])
        y_values.append(i[y_column])

    return {"chart_name": chart_name, "x_values": x_values, "y_values": y_values}


