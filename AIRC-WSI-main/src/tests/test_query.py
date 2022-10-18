def test_document_count(client):
    response = client.get('/query/document_count')
    assert b"Total Documents" in response.data
    assert b"Total Publications" in response.data
    assert b"Total Patents" in response.data
