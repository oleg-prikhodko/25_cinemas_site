import os
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

ONE_HOUR_IN_SECS = 60 * 60
DEFAULT_PORT = 5000


@app.route("/")
def films_list():
    return render_template("films_list.html")


@app.route("/api/movies")
@cache.cached(timeout=ONE_HOUR_IN_SECS)
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
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    debug = bool(os.environ.get("FLASK_DEBUG", False))
    app.run(host="0.0.0.0", port=port, debug=debug)
