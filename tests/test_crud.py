from backend.routes import collection

def test_read_and_validation(client):
    assert client.get('/health').json == {'status': 'OK'}
    assert len(client.get('/song').json) == 20
    assert client.get('/song/1').json['id'] == 1
    assert client.get('/song/9999').status_code == 404
    assert client.post('/song', json={}).status_code == 400

def test_song_lifecycle(client):
    song = {'id': 200, 'title': 'Capstone Song', 'lyrics': 'A real API test'}
    assert client.post('/song', json=song).status_code == 201
    assert client.post('/song', json=song).status_code == 302
    song['lyrics'] = 'Updated lyrics'
    assert client.put('/song/200', json=song).status_code == 200
    assert client.get('/song/200').json['lyrics'] == 'Updated lyrics'
    assert client.delete('/song/200').status_code == 204
    assert client.get('/song/200').status_code == 404
    assert client.delete('/song/200').status_code == 404
    assert client.put('/song/200', json=song).status_code == 404
