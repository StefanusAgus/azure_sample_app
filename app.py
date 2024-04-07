from dotenv import load_dotenv
from flask import Flask, jsonify, request

import os
import pymongo

# Load environment variables from .env file
load_dotenv()

# Setup flask environment and DB connector
app = Flask(__name__)

COSMOS_CONNECTION_STRING = os.getenv('COSMOS_CONNECTION_STRING', 'development')
cosmos_client = pymongo.MongoClient(COSMOS_CONNECTION_STRING)


@app.route('/home', methods=['GET'])
def home():
    lorem_ipsum = {
        "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    }
    return jsonify(lorem_ipsum)


@app.route('/', methods=['GET'])
def base():
    return "hello world"


@app.route('/list_collection', methods=['GET'])
def list_collection():
    db_name = request.args.get("db_name")
    if db_name not in cosmos_client.list_database_names():
        return f"Database {db_name} does not exist"
    try:
        db = cosmos_client[db_name]
        return "\n".join(db.list_collection_names())
    except Exception as e:
        return f"List collection exception: {e}"


@app.route('/list_database', methods=['GET'])
def list_database():
    database_names = cosmos_client.list_database_names()
    return "\n".join(database_names)


@app.route('/create_database', methods=['POST'])
def create_database():
    data = request.get_json()
    database_name = data.get('database_name')

    if database_name:
        if database_name in cosmos_client.list_database_names():
            return jsonify({'message': f'Database "{database_name}" already exists'}), 409
        else:
            db = cosmos_client[database_name]
            # Perform custom action to create database with offerThroughput 400
            db.command({"customAction": "CreateDatabase", "offerThroughput": 400})
            return jsonify({'message': f'Database "{database_name}" created successfully'})
    else:
        return jsonify({'error': 'Database name not provided'}), 400


@app.route('/create_collection', methods=['POST'])
def create_collection():
    data = request.get_json()
    database_name = data.get('database_name')
    collection_name = data.get('collection_name')

    if database_name and collection_name:
        db = cosmos_client[database_name]
        if collection_name in db.list_collection_names():
            return jsonify({'message': f'Collection "{collection_name}" already exists'}), 409
        else:
            # Create the collection using custom action
            db.command({"customAction": "CreateCollection", "collection": collection_name})
            return jsonify({'message': f'Collection "{collection_name}" created successfully'})
    else:
        return jsonify({'error': 'Database or collection name not provided'}), 400


# @app.route('/create_index', methods=['POST'])
# def create_index():
#     # Access JSON data from the request body
#     data = request.json
#     # Process the data or perform any necessary actions
#     # For example, you could save the data to a database
#     return "Index created successfully"

if __name__ == '__main__':
    app.run(debug=True)
