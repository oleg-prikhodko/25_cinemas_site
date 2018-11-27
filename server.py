from flask import Flask, render_template, jsonify
from flask_caching import Cache
import cinemas

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'filesystem'})

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
        }
        for title, rating_value, rating_count in cinemas.get_movies()
    ]
    return jsonify(movies)


if __name__ == "__main__":
    app.run()
