import os
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey, Table
from flask_sqlalchemy import SQLAlchemy
import json
from flask_migrate import Migrate

database_name = "capstone"
database_path = "postgres://{}@{}/{}".format('capstone:capstone','localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)


def db_drop_and_create_all():
    """drops the database tables and starts fresh
    can be used to initialize a clean database"""
    db.drop_all()
    db.create_all()

# there'll need to be a many-to-many relationship between movies and actors
# this is a helper table for the relationship
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
movie_actor_table = Table('movie_actor_table', db.Model.metadata,
                            Column('movie_id', Integer, ForeignKey('movies.id')),
                            Column('actor_id', Integer, ForeignKey('actors.id')))


class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(80), unique=True, nullable=False)
    release_date = Column(Integer)
    actors = db.relationship('Actor', secondary=movie_actor_table,
                             backref='actors_list', lazy=True)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()
  
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
          'id': self.id,
          'title': self.title,
          'release_date': self.release_date,
    }


class Actor(db.Model):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    movies = db.relationship('Movie', secondary=movie_actor_table,
                             backref='movies_list', lazy=True)

    
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()
  
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
          'id': self.id,
          'name': self.name,
          'gender': self.gender,
    }