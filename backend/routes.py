"""Song API. MongoDB in deployment; explicit in-memory Mongo mock for local tests."""
import os
import json
from pathlib import Path
from urllib.parse import quote_plus
from flask import jsonify, request
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from . import app

if os.environ.get('MONGODB_MOCK') == '1':
    from mongomock import MongoClient
    client = MongoClient()
else:
    uri = os.environ.get('MONGODB_URI')
    if not uri:
        host = os.environ.get('MONGODB_SERVICE', 'localhost')
        port = os.environ.get('MONGODB_PORT', '27017')
        user, password = os.environ.get('MONGODB_USERNAME'), os.environ.get('MONGODB_PASSWORD')
        auth = f'{quote_plus(user)}:{quote_plus(password)}@' if user and password else ''
        uri = f'mongodb://{auth}{host}:{port}'
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
collection = client.songs.songs
collection.create_index([('id', ASCENDING)], unique=True)
# Seed only missing records. Do not erase persistent user changes at startup.
if collection.count_documents({}) == 0:
    collection.insert_many(json.loads((Path(__file__).parent / 'data/songs.json').read_text()))

def clean(document):
    if document is not None:
        return {k: v for k, v in document.items() if k != '_id'}

def payload():
    obj = request.get_json(silent=True)
    if not isinstance(obj, dict) or not all(k in obj for k in ('id', 'title', 'lyrics')):
        return None
    if not isinstance(obj['id'], int) or isinstance(obj['id'], bool) or obj['id'] < 1:
        return None
    if not all(isinstance(obj[k], str) and obj[k].strip() for k in ('title', 'lyrics')):
        return None
    return {k: obj[k] for k in ('id', 'title', 'lyrics')}

@app.get('/health')
def health():
    client.admin.command('ping')
    return jsonify(status='OK'), 200

@app.get('/count')
def count():
    return jsonify(length=collection.count_documents({})), 200

@app.get('/song')
def get_songs():
    return jsonify([clean(s) for s in collection.find().sort('id', 1)]), 200

@app.get('/song/<int:id>')
def get_song_by_id(id):
    song = clean(collection.find_one({'id': id}))
    return (jsonify(song), 200) if song else (jsonify(Message='song not found'), 404)

@app.post('/song')
def create_song():
    song = payload()
    if song is None:
        return jsonify(Message='Invalid song payload'), 400
    try:
        collection.insert_one(dict(song))
    except DuplicateKeyError:
        return jsonify(Message=f"song with id {song['id']} already present"), 302
    return jsonify(song), 201, {'Location': f"/song/{song['id']}"}

@app.put('/song/<int:id>')
def update_song(id):
    song = payload()
    if song is None or song['id'] != id:
        return jsonify(Message='Invalid song payload or mismatched id'), 400
    result = collection.replace_one({'id': id}, song)
    return (jsonify(song), 200) if result.matched_count else (jsonify(Message='song not found'), 404)

@app.delete('/song/<int:id>')
def delete_song(id):
    result = collection.delete_one({'id': id})
    return ('', 204) if result.deleted_count else (jsonify(Message='song not found'), 404)
