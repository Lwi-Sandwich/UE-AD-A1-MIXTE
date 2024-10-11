import json

def movie_with_id(_, info, _id):
    with open('./data/movies.json', 'r') as file:
        movies = json.load(file)['movies']
        for m in movies:
            if m['id'] == _id:
                return m

def update_movie_rate(_, info, _id, _rate):
    with open('./data/movies.json', 'r') as f:
        movies = json.load(f)['movies']
        for m in movies:
            if m['id'] == _id:
                m['rating'] = _rate
                with open('./data/movies.json', 'w') as f:
                    json.dump({'movies': movies}, f)
                return m

def resolve_actors_in_movie(movie, info):
    with open('./data/actors.json', 'r') as f:
        actors = json.load(f)['actors']
        result = [actor for actor in actors if movie['id'] in actor['films']]
        return result

def actor_with_id(_, info, _id):
    with open('./data/actors.json', 'r') as file:
        actors = json.load(file)['actors']
        for a in actors:
            if a['id'] == _id:
                return a

def movies(_, info):
    with open('./data/movies.json', 'r') as file:
        movies = json.load(file)['movies']
        return movies