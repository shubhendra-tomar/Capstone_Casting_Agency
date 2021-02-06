import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from  models import setup_db, db_drop_and_create_all, Movie, Actor, db


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  return app

APP = create_app()

#app = Flask(__name__)
#setup_db(app)


'''
Use the after_request decorator to set Access-Control-Allow
'''
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allowed-Headers','Content-Type, Authorization')
  response.headers.add('Access-Control-Allowed-Methods','GET, POST, PATCH, DELETE')
  return response


@app.route('/movies')
def get_movies(payload):
    try:
      movies = Movie.query.all()
      if len(movies) == 0:
          abort(404)
      movies_list = [movie.format() for movie in movies]
      return jsonify({
            'success': True,
            'movies': movies_list
        }), 200
    except:
      abort(422)


@app.route('/actors')
def get_actors(payload):
    try:
      actors = Actor.query.all()
      if len(actors) == 0:
          abort(404)
      actors_list = [actor.format() for actor in actors]
      return jsonify({
            'success': True,
            'actors': actors_list
        }), 200
    except:
      abort(422)


@app.route('/movies', methods=['POST'])
def add_movie(payload):
    new_title = request.get_json().get('title')
    new_release_date = request.get_json().get('release_date')
      
    # check if all fields have data
    if ((new_title is None) or (new_release_date is None)):
          abort(400)

    movie = Movie(title=new_title,release_date=new_release_date)

    try:
      movie.insert()
    except:
      db.session.rollback()
      abort(422)

    return jsonify({
      'success' : True,
      'movie': movie.format()
    }), 200


@app.route('/movies/<int:movie_id>', methods=['PATCH'])
def update_movie(payload, movie_id):
    title = request.get_json().get('title')
    release_date = request.get_json().get('release_date')

    # check if all fields have data
    if ((title is None) or (release_date is None)):
          abort(400)

    # make sure movie exists
    movie = Movie.query.filter_by(id=movie_id).first()
    if not movie:
        abort(404)

    movie.title = title
    movie.release_date = release_date    

    # update
    try:
        movie.update()
    except:
      db.session.rollback()
      abort(422)

    return jsonify({
        'success': True,
        'movie': movie.format()
    }), 200



if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)