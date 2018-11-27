import logging
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup


def fetch_afisha_page(url="https://www.afisha.ru/msk/schedule_cinema/"):
    response = requests.get(url)
    html = response.text
    return html


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    cards = soup.select("div.card.cards-grid__item")
    afisha_movie_infos = [
        (
            card.select_one("h3.card__title").string.strip(),
            "https://www.afisha.ru{}".format(
                card.select_one("a.card__link")["href"]
            ),
            card.select_one("img.card__image")["src"],
        )
        for card in cards
    ]
    return afisha_movie_infos


def fetch_movie_info(movie_title):
    movie_title = re.sub(r"«|»", "", movie_title)
    url = "https://www.kinopoisk.ru/index.php"
    params = {"kp_query": movie_title}
    response = requests.get(url, params=params)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    non_breaking_space = "\u00A0"
    page_title = soup.title.string.strip()
    most_wanted = soup.select_one(".most_wanted")

    if most_wanted is not None:
        link = most_wanted.select_one("div.info > p > a")
        title = link.string.strip()
        if title not in movie_title:
            logging.warning("Could not find movie {}".format(movie_title))
            return None
        rating = most_wanted.select_one(".rating")
        if rating is None:
            return "—", "—"
        rating = rating["title"].replace(non_breaking_space, "")
        match = re.search(r"(\d\.\d*) \((\d*)\)", rating)
        value_group_index = 1
        count_group_index = 2
        rating_value = match.group(value_group_index)
        rating_count = match.group(count_group_index)
        return rating_value, rating_count

    elif movie_title in page_title:
        rating_value = soup.find("meta", attrs={"itemprop": "ratingValue"})[
            "content"
        ]
        rating_count = soup.find("meta", attrs={"itemprop": "ratingCount"})[
            "content"
        ]
        return rating_value, rating_count

    else:
        logging.warning("Could not find movie {}".format(movie_title))
        return None


def sort_movies_by_rating(movies):
    default_rating = 0.0
    rating_value_index = 3
    return sorted(
        movies,
        key=lambda movie: float(movie[rating_value_index])
        if re.search(r"\d\.\d*", movie[rating_value_index]) is not None
        else default_rating,
        reverse=True,
    )


def output_movies_to_console(movies):
    for movie in movies:
        print("{} | {} | {} | {} | {}".format(*movie))


def get_movies(max_movies=10):
    try:
        html = fetch_afisha_page()
        afisha_infos = parse_afisha_list(html)
        title_index = 0
        titles = list(map(lambda info: info[title_index], afisha_infos))
        executor = ThreadPoolExecutor()
        kinopoisk_infos = executor.map(fetch_movie_info, titles)
        movies = [
            (*afisha_info, *kinopoisk_info)
            for afisha_info, kinopoisk_info in zip(
                afisha_infos, kinopoisk_infos
            )
            if kinopoisk_info is not None
        ]
        movies = sort_movies_by_rating(movies)[:max_movies]
        return movies
    except requests.RequestException as err:
        sys.exit(err)


if __name__ == "__main__":
    movies = get_movies()
    output_movies_to_console(movies)
