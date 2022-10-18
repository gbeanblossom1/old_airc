This file documents available endpoints for the tb_api (Threat Beacon WSI). It outlines what each endpoint expects and can accept as parameters and what data is returned. Endpoints are categorized by flask blueprint. 

BRICC Server Development URLS:

- 192.168.10.105:5010/ - Displays available endpoints collections (blueprints)
- 192.168.10.105:5010/query - Displays endpoints in "query" blueprint (includes param list)
- 192.168.10.105:5010/schema - Dsplays endpoint schema locations


- [Query Endpoints](#query-endpoints)


# Query Endpoints

/query/*


<table>
    <tr>
        <td> Endpoint </td> <td> Details </td> <td> Parameters </td> <td> Example </td> <td> Return </td> 
    </tr>
    <tr>
        <td> document_count </td> 
        <td> Returns document counts at three levels: by total documents, by document type, and by data source. </td> 
        <td> None </td> 
        <td> https://localhost:5000/query/document_count </td> 
<td> 
    A list of json objects. Note: "indent" is an optional indentation factor that can be used to determine how much to indent the labels if you want to display a hierarchy of document counts.
    
    [        
        {
            "label": "Total Documents"
            "value" 1000000
            "indent": 0
        },
        {
            "label": "Total Publications"
            "value" 500000
            "indent": 1
        },
        {
            "label": "Scopus"
            "value" 300000
            "indent": 2
        },
        ...
    ]
           
            
</td>
    </tr>
    
</table>




