import json
import os
from pymongo import MongoClient

def lambda_handler(event, context):
    try:
        userinput = event['queryStringParameters'].get("name")
        if not userinput:
            return {
                'statusCode': 200,
                'body': json.dumps([])
            }
        
        client = MongoClient("mongodb+srv://" + os.environ["MONGO_USER"] + ":" + os.environ["MONGO_PWD"] + "@cluster0.tnymq.mongodb.net/?retryWrites=true&w=majority")
        db = client['recommender']
        collection = db['movie_recommendation_tmdb']

        pipeline = [
            {
                "$search": {
                    "autocomplete": {
                        "query": userinput,
                        "path": "title",
                    }
                }
            },
            {
                "$limit": 10
            },
            {
                "$project": {
                    "title": 1,
                    "tmdbId": 1,
                    "_id": 0
                }
            }
        ]
        results = list(collection.aggregate(pipeline))
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps([])
        }
