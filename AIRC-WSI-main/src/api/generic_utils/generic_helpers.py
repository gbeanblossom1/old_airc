from elastipy import search

###################
# RESPONSE OBJECT #
###################

def set_endpoint_response(success=None, message="", status_code=200, results=[]):
    if success is None:
        response = {"success": True, "message": message, "status_code": status_code, "results": results}
    else:
        response = {"success": success, "message": message, "status_code": status_code, "results": results}
    return response

def set_helper_response(response=None, success=True, message=""):
    if response is None:
        response = {"success": True, "message": ""}
    else:
        response["success"] = success
        response["message"] = message

    return response

    