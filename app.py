import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, db_drop_and_create_all, Movie, Actor, db
from auth import requires_auth, AuthError

'''
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  return app

APP = create_app()
'''
app = Flask(__name__)
setup_db(app)


'''
Use the after_request decorator to set Access-Control-Allow
'''
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allowed-Headers','Content-Type, Authorization')
  response.headers.add('Access-Control-Allowed-Methods','GET, POST, PATCH, DELETE')
  return response


@app.route('/movies')
@requires_auth('get:movies')
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
@requires_auth('get:actors')
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
@requires_auth('post:movies')
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



@app.route('/actors', methods=['POST'])
@requires_auth('post:actors')
def add_actor(payload):
    new_name = request.get_json().get('name')
    new_age = request.get_json().get('age')
    new_gender = request.get_json().get('gender')
      
    # check if all fields have data
    if ((new_name is None) or (new_age is None) or (new_gender is None)):
          abort(400)

    actor = Actor(name=new_name, age=new_age, gender=new_gender)

    try:
      actor.insert()
    except:
      db.session.rollback()
      abort(422)

    return jsonify({
      'success' : True,
      'actor': actor.format()
    }), 200



@app.route('/movies/<int:movie_id>', methods=['PATCH'])
@requires_auth('patch:movies')
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



@app.route('/actors/<int:actor_id>', methods=['PATCH'])
@requires_auth('patch:actors')
def update_actor(payload, actor_id):
    name = request.get_json().get('name')
    age = request.get_json().get('age')
    gender = request.get_json().get('gender')

    # check if all fields have data
    if ((name is None) or (age is None) or (gender is None)):
          abort(400)

    # make sure movie exists
    actor = Actor.query.filter_by(id=actor_id).first()
    if not actor:
        abort(404)

    actor.name = name
    actor.age = age
    actor.gender = gender    

    # update
    try:
        actor.update()
    except:
      db.session.rollback()
      abort(422)

    return jsonify({
        'success': True,
        'actor': actor.format()
    }), 200


'''
error handler for AuthError
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


'''
  Create error handlers for all expected errors 
  including 404 and 422. 
'''
@app.errorhandler(404)
def not_found(error):
  return jsonify({
    "success": False,
    "error": 404,
    "message": "resource not found"
  }), 404

@app.errorhandler(422)
def unprocessable(error):
  return jsonify({
    "success": False,
    "error": 422,
    "message": "unprocessable"
  }), 422

@app.errorhandler(400)
def bad_request(error):
  return jsonify({
    "success": False,
    "error": 400,
    "message": "bad request"
  }), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)