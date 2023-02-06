import json
import requests
import os
from pymongo import MongoClient

def recommendation(event, context):
    try:
        tmdbId = int(event.get("queryStringParameters", {}).get("id", 0))
        if tmdbId == 0:
          return {
              'statusCode': 400,
              'body': {}
        }
        page = int(event.get("queryStringParameters", {}).get("p", 1))
        per_page = 12

        if page < 1 or page > 3:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid page number. Page number should be between 1 and 3"})
            }
        
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        tmdb_key = os.environ['TMDB_ACCESS_KEY']

        client = MongoClient("mongodb+srv://" + os.environ["MONGO_USER"] + ":" + os.environ["MONGO_PWD"] + "@cluster0.tnymq.mongodb.net/?retryWrites=true&w=majority")
        db = client['recommender']
        collection = db['movie_recommendation_tmdb']


        recommended_movies = collection.find_one({"tmdbId": tmdbId})
        if recommended_movies:
          recommended_movies = recommended_movies["recommended_movies"][start_index:end_index]
        else:
          return {
            "statusCode": 500,
            "body": json.dumps({"error": "The data for this movie is currently not available. Please try again later or reach out for further assistance."})
          }

        is_error = False
        tmdb_data = []
        for d in recommended_movies:
            try:
                response = requests.get(f"https://api.themoviedb.org/3/movie/{d}?api_key={tmdb_key}")
                if response.status_code == 200:
                    tmdb_data.append(response.json())
                else:
                    pass
            except:
                is_error = True
                break
        if is_error:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Unable to connect to TMDB API"})
            }
        else:
            try:
                response = requests.get(f"https://api.themoviedb.org/3/movie/{tmdbId}?api_key={tmdb_key}")
                if response.status_code == 200:
                    original_title = response.json()["original_title"]
                else:
                    pass
            except:
                is_error = True
            if is_error:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Unable to connect to TMDB API"})
                }
            else:
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "movie_list": tmdb_data,
                        "movie_count": len(tmdb_data),
                        "searched_movie_title": original_title
                    })
                }

    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error", "message": "An error has occured, please try again later"})
        }
