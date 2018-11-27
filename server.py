from os.path import abspath, dirname, join

from flask import Flask, jsonify, render_template
from flask_caching import Cache

import cinemas

app = Flask(__name__)
cache = Cache(
    app,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": join(dirname(abspath(__name__)), "cache"),
    },
)


@app.route("/")
def films_list():
    return render_template("films_list.html")


@app.route("/api/movies")
@cache.cached(timeout=50)
def get_movies():
    movies = [
        {
            "title": title,
            "rating_value": rating_value,
            "rating_count": rating_count,
            "url": url,
            "image_url": image_url,
        }
        for title, url, image_url, rating_value, rating_count in cinemas.get_movies()
    ]
    return jsonify(movies)


if __name__ == "__main__":
    app.run()
