import os
import sqlite3
from flask import Flask, render_template, request
import requests

# Initialize the Flask app
app = Flask(__name__)

# TMDB API key and read token
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_READ_TOKEN = os.getenv("TMDB_READ_TOKEN")

# Base URL
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Route for the homepage
@app.route("/")
def home():
    page = int(request.args.get("page", 1))
    limit = 21
    offset = (page - 1) * limit

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT imdb_id FROM movies LIMIT ? OFFSET ?", (limit, offset))
    imdb_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    filtered_movies = get_tmdb_data(imdb_ids)

    all_triggers = get_all_triggers()
    return render_template("home.html", movies=filtered_movies, all_triggers=all_triggers)

# Get trigger definitions
def get_all_triggers():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, name
        FROM trigger_definitions
        ORDER BY category, name
    """)
    grouped = {}
    for category, name in cursor.fetchall():
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(name)
    conn.close()
    return grouped


# Get movie details from TMDB with IMDB ID
def get_tmdb_data(imdb_ids):
    headers = {
        "Authorization": f"Bearer {TMDB_READ_TOKEN}",
        "Accept": "application/json"
    }

    filtered_movies = []

    for imdb_id in imdb_ids:
        if not imdb_id:
            continue

        find_url = f"{TMDB_BASE_URL}/find/{imdb_id}"
        params = {"external_source": "imdb_id"}
        response = requests.get(find_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            results = data.get("movie_results", [])
            if results:
                movie = results[0]
                movie_id = movie["id"]

                #get movie details
                details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
                details_params = {"api_key": TMDB_API_KEY, "language": "en-US"}
                details_response = requests.get(details_url, params=details_params)
                if details_response.status_code == 200:
                    full_movie = details_response.json()
                    full_movie["imdb_id"] = imdb_id
                    filtered_movies.append(full_movie)
        else:
            print(f"TMDB error for {imdb_id}: {response.status_code}")
    print(f"Matched {len(filtered_movies)} local movies to TMDB metadata")

    return filtered_movies

# Load more movies when scrolling down
@app.route("/load_more")
def load_more():
    page = int(request.args.get("page", 1))
    query = request.args.get("q", "").strip().lower()

    limit = 21
    offset = (page - 1) * limit

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    if query:
        cursor.execute("""
            SELECT imdb_id FROM movies WHERE LOWER(title) LIKE ? LIMIT ? OFFSET ?
        """, (f"%{query}%", limit, offset))
    else:
        cursor.execute("SELECT imdb_id FROM movies LIMIT ? OFFSET ?", (limit, offset))

    imdb_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    movies = get_tmdb_data(imdb_ids)
    return render_template("partials/movie_cards.html", movies=movies)

# Search function for movies
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip().lower()
    page = int(request.args.get("page", 1))
    limit = 21
    offset = (page - 1) * limit

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT imdb_id FROM movies
        WHERE LOWER(title) LIKE ?
        LIMIT ? OFFSET ?
    """, (f"%{query}%", limit, offset))
    imdb_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    matched_movies = get_tmdb_data(imdb_ids)

    return render_template("search_results.html", query=query, movies=matched_movies)

# Get movie details when movie is selected
@app.route("/movie/<int:movie_id>")
def movie_details(movie_id):
    selected_triggers = request.args.getlist("triggers")

    # Fetch movie details from TMDB
    movie_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    credits_url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}

    movie = requests.get(movie_url, params=params).json()
    credits = requests.get(credits_url, params=params).json()

    crew = credits.get("crew", [])
    director = next((member["name"] for member in crew if member["job"] == "Director"), "Unknown")
    imdb_id = movie.get("imdb_id")
    imdb_link = f"https://www.imdb.com/title/{imdb_id}"
    genres = ", ".join([genre["name"] for genre in movie.get("genres", [])])
    synopsis = movie.get("overview", "No synopsis available.")
    poster_url = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}"

    # Get movie_id from local database
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM movies WHERE imdb_id = ?", (imdb_id,))
    row = cursor.fetchone()
    triggers_to_display = []

    if row:
        local_movie_id = row[0]
        # Only fetch triggers that are both selected AND have value=1
        placeholders = ",".join("?" for _ in selected_triggers) or "''"
        sql = f"""
            SELECT td.name
            FROM triggers t
            JOIN trigger_definitions td ON t.trigger_id = td.id
            WHERE t.movie_id = ? AND t.value = 1 AND td.name IN ({placeholders})
        """
        cursor.execute(sql, (local_movie_id, *selected_triggers))
        triggers_to_display = [row[0] for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "movie_details.html",
        title=movie.get("title"),
        imdb_link=imdb_link,
        genres=genres,
        director=director,
        synopsis=synopsis,
        poster_url=poster_url,
        triggers=triggers_to_display 
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)