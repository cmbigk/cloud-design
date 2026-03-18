"""
Inventory routes module.
Handles movie resource management (CRUD operations).
"""
from flask import request, jsonify

from app import app, db
from app.models import Movie


@app.route("/movies", methods=["GET"], strict_slashes=False)
def get_movies():
    """
    Retrieve a list of movies.
    Supports optional 'title' query parameter for filtering.
    """

    title = request.args.get("title")
    if title:
        movies = Movie.query.filter(Movie.title.ilike(f"%{title}%")).all()
    else:
        movies = Movie.query.all()
    return jsonify([movie.to_dict() for movie in movies]), 200


@app.route("/movies", methods=["DELETE"], strict_slashes=False)
def delete_all_movies():
    """
    Delete all movie records from the database.
    """

    db.session.query(Movie).delete()
    db.session.commit()
    return jsonify({"message": "All movies deleted"}), 200


@app.route("/movies", methods=["POST"], strict_slashes=False)
def add_movie():
    """
    Add a new movie record to the database.
    Requires 'title' in JSON body.
    """

    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    new_movie = Movie(title=data["title"], description=data.get("description", ""))
    db.session.add(new_movie)
    db.session.commit()
    return jsonify(new_movie.to_dict()), 201


@app.route("/movies/<int:movie_id>", methods=["GET"], strict_slashes=False)
def get_movie(movie_id):
    """
    Retrieve details for a single movie by ID.
    """

    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    return jsonify(movie.to_dict()), 200


@app.route("/movies/<int:movie_id>", methods=["PUT"], strict_slashes=False)
def update_movie(movie_id):
    """
    Update an existing movie record by ID.
    Supports updating 'title' and 'description'.
    """

    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    data = request.get_json()
    if "title" in data:
        movie.title = data["title"]
    if "description" in data:
        movie.description = data["description"]
    db.session.commit()
    return jsonify(movie.to_dict()), 200


@app.route("/movies/<int:movie_id>", methods=["DELETE"], strict_slashes=False)
def delete_movie(movie_id):
    """
    Delete a single movie record by ID.
    """

    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    db.session.delete(movie)
    db.session.commit()
    return jsonify({"message": "Movie deleted"}), 200
