import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, db_drop_and_create_all, Movie, Actor, db
from auth import requires_auth, AuthError
import datetime


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  '''
  app = Flask(__name__)
  setup_db(app)
  '''

  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allowed-Headers',
                              'Content-Type, Authorization')
    response.headers.add('Access-Control-Allowed-Methods',
                              'GET, POST, PATCH, DELETE')
    return response

  '''
  GET /movies
  - to get all existing movies
  - to check JWT and permissions
  - to return list of movies in case of success 
      else return appropriate error code
  '''
  @app.route('/movies')
  @requires_auth('get:movies')
  def get_movies(payload):
      try:
        movies = Movie.query.all()
        # to return 404 in case no data found
        if len(movies) == 0:
            abort(404)
        # form a list of movies and return in response
        movies_list = [movie.format() for movie in movies]
        return jsonify({
              'success': True,
              'movies': movies_list
          }), 200
      except Exception:
        abort(422)


  '''
  GET /actors
  - to get all existing actors
  - to check JWT and permissions
  - to return list of actors in case of success 
      else return appropriate error code
  '''
  @app.route('/actors')
  @requires_auth('get:actors')
  def get_actors(payload):
      try:
        actors = Actor.query.all()
        # to return 404 in case no data found
        if len(actors) == 0:
            abort(404)
        # form a list of actors and return in response
        actors_list = [actor.format() for actor in actors]
        return jsonify({
              'success': True,
              'actors': actors_list
          }), 200
      except Exception:
        abort(422)


  '''
  POST /movies
  - to add new movie to the database
  - to check JWT and permissions to add a movie
  - to return added movie in case of success 
      else return appropriate error code
  '''
  @app.route('/movies', methods=['POST'])
  @requires_auth('post:movies')
  def add_movie(payload):
      new_title = request.get_json().get('title')
      new_release_date = request.get_json().get('release_date')
      # check if all fields have data
      if ((new_title is None) or (new_release_date is None)):
            abort(400)

      # check to find if movie already exists
      movie_check = Movie.query.filter(Movie.title == new_title).one_or_none()
      if movie_check:
            abort(409)

      try:
        date_obj = datetime.datetime.strptime(new_release_date, '%Y-%m-%d')
      except ValueError:
        raise AuthError({
          'code': 'invalid_format',
          'description': 'For release date use this format YYYY-MM-DD'
        }, 400)
          
      movie = Movie(title=new_title,release_date=new_release_date)
      try:
        movie.insert()
        db.session.rollback()
      except Exception:
        db.session.rollback()
        abort(422)

      return jsonify({
        'success' : True,
        'movie': movie.format()
      }), 200


  '''
  POST /actors
  - to add new actors to the database
  - to check JWT and permissions to add a actor
  - to return added actor in case of success 
      else return appropriate error code
  '''
  @app.route('/actors', methods=['POST'])
  @requires_auth('post:actors')
  def add_actor(payload):
      new_name = request.get_json().get('name')
      new_age = request.get_json().get('age')
      new_gender = request.get_json().get('gender')
      
      # check if all fields have data
      if ((new_name is None) or (new_age is None) 
                              or (new_gender is None)):
            abort(400)

      actor = Actor(name=new_name, age=new_age, gender=new_gender)

      try:
        actor.insert()
      except Exception:
        # to rollback in case of exception  
        db.session.rollback()
        abort(422)

      return jsonify({
        'success' : True,
        'actor': actor.format()
      }), 200


  '''
  PATCH /movies/<id>
  - where id is movie id of existing movie
  - to update movie details to the database
  - to check JWT and permissions to update a movie
  - to return updated movie detail in case of success 
      else return appropriate error code
  '''
  @app.route('/movies/<int:movie_id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def update_movie(payload, movie_id):
      title = request.get_json().get('title')
      release_date = request.get_json().get('release_date')

      # make sure movie exists
      movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
      if not movie:
          abort(404)

      if ((title is None) and (release_date is None)):
          abort(400)

      # check which field to be updated
      if (title is not None):
          movie.title = title
      elif (release_date is not None):
          movie.release_date = release_date

      try:
          date_obj = datetime.datetime.strptime(release_date, '%Y-%m-%d')
      except ValueError:
          raise AuthError({
            'code': 'invalid_format',
            'description': 'For release date use this format YYYY-MM-DD'
          }, 400)

      # update
      try:
          movie.update()
      except:
        # Rollback in case of exception
        db.session.rollback()
        abort(422)

      return jsonify({
          'success': True,
          'movie': movie.format()
      }), 200


  '''
  PATCH /actors/<id>
  - where id is actor id of existing actor
  - to update actor details to the database
  - to check JWT and permissions to update a actor
  - to return updated actor detail in case of success 
      else return appropriate error code
  '''
  @app.route('/actors/<int:actor_id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def update_actor(payload, actor_id):
      name = request.get_json().get('name')
      age = request.get_json().get('age')
      gender = request.get_json().get('gender')

      # make sure actor exists
      actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
      if not actor:
          abort(404)

      
      if ((name is None) and (age is None) and (gender is None)):
            abort(400)
      
      # check which fields to update
      if (name is not None):
        actor.name = name
      if (age is not None):
        actor.age = age
      if (gender is not None):
        actor.gender = gender    

      # update
      try:
          actor.update()
      except Exception:
        # rollback changes in case of exception
        db.session.rollback()
        abort(422)

      return jsonify({
          'success': True,
          'actor': actor.format()
      }), 200


  '''
  DELETE /movies/<id>
  - where id is movie id of existing movie
  - to delete movie details from the database
  - to check JWT and permissions to delete a movie
  - returns status code 200 and json {"success": True, "delete": id}
      where id is the id of the deleted record
      or appropriate status code indicating reason for failure
  '''
  @app.route('/movies/<int:movie_id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movie(payload, movie_id):
      # make sure actor exists
      movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

      if not movie:
          abort(404)

      # delete movie details
      try:
          movie.delete()
      except Exception:
          # to rollback changes in case of exception
          db.session.rollback()
          abort(400)

      return jsonify({
          'success': True,
          'delete': movie_id
      }), 200


  '''
  DELETE /actors/<id>
  - where id is actor id of existing actor
  - to delete actor details from the database
  - to check JWT and permissions to delete a actor
  - returns status code 200 and json {"success": True, "delete": id}
      where id is the id of the deleted record
      or appropriate status code indicating reason for failure
  '''
  @app.route('/actors/<int:actor_id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_drink(payload, actor_id):
      # make sure actor exists
      actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

      if not actor:
          abort(404)

      # delete actor details from database
      try:
          actor.delete()
      except Exception:
          db.session.rollback()
          abort(400)

      return jsonify({
          'success': True,
          'delete': actor_id
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
  error handler for resource not found
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
    }), 404

  '''
  error handler for unprocessable entity
  '''
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
    }), 422

  '''
  error handler for bad request
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400

  '''
  error handler for data conflict
  '''
  @app.errorhandler(409)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 409,
      "message": "Conflict , title already exists"
    }), 409

  '''
  error handler for Unauthorized
  '''
  @app.errorhandler(401)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 401,
      "message": "Unauthorized access"
    }), 401

  return app

app=create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)