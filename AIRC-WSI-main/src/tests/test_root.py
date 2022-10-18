import json

def test_root(client):
    response = client.get('/')
    # import pdb; pdb.set_trace()
    json_data = json.loads(response.data)
    assert len(json_data["features"]) > 0
    assert "/query" in json_data['features'][0]['path']


def test_query_root(client):
    response = client.get('/query/')
    json_data = json.loads(response.data)
    assert len(json_data['endpoints']) > 0
