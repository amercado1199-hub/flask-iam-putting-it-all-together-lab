#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema


class Signup(Resource):

    def post(self):
        data = request.get_json()

        try:
            user = User(
                username=data.get('username'),
                bio=data.get('bio'),
                image_url=data.get('image_url')
            )

            user.password_hash = data.get('password')

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return UserSchema().dump(user), 201

        except (ValueError, IntegrityError):
            db.session.rollback()
            return {'errors': ['validation errors']}, 422


class CheckSession(Resource):

    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return UserSchema().dump(user), 200

        return {}, 401


class Login(Resource):

    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return UserSchema().dump(user), 200

        return {'error': 'Invalid username or password'}, 401


class Logout(Resource):

    def delete(self):

        if not session.get('user_id'):
            return {}, 401

        session.clear()

        return {}, 204


class RecipeIndex(Resource):

    def get(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401

        recipes = [RecipeSchema().dump(recipe) for recipe in Recipe.query.all()]
        return recipes, 200

    def post(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()

        try:
            recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=session.get('user_id')
            )

            db.session.add(recipe)
            db.session.commit()

            return RecipeSchema().dump(recipe), 201

        except ValueError:
            db.session.rollback()
            return {'errors': ['validation errors']}, 422


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)