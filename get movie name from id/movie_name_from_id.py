import os
import pymongo
import json

def lambda_handler(event, context):
    try:
        tmdbId = int(event['queryStringParameters'].get("tmdbId", 0))
        if tmdbId == 0:
          return {
              'statusCode': 400,
              'body': {}
        }
        client = pymongo.MongoClient("mongodb+srv://" + os.environ["MONGO_USER"] + ":" + os.environ["MONGO_PWD"] + "@cluster0.tnymq.mongodb.net/?retryWrites=true&w=majority")
        db = client['recommender']
        collection = db['movie_recommendation_tmdb']
        title = collection.find_one({"tmdbId": tmdbId},{"_id":0, "title":1})
        return {
            'statusCode': 200,
            'body': json.dumps(title)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {}
        }


