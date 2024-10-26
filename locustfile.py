from locust import HttpUser, task, between
import random


class WebsiteUser(HttpUser):
    wait_time = between(1, 2.5)

    clubs = [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {
            "name": "Iron Temple",
            "email": "admin@irontemple.com",
            "points": "4"
        },
        {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"}
    ]

    competitions = [
        {
            "name": "Spring Festival",
            "date": "2025-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Fall Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
        }
    ]

    @task
    def load_main(self):
        self.client.get("/")

    @task
    def load_showSummary(self):
        club = random.choice(self.clubs)
        self.client.post("/showSummary", {"email": club["email"]})

    @task
    def load_book(self):
        competition = random.choice(self.competitions)
        club = random.choice(self.clubs)
        self.client.get(
            f"/book/{competition['name']}/{club['name']}"
        )

    @task
    def load_purchasePlaces(self):
        competition = random.choice(self.competitions)
        club = random.choice(self.clubs)
        self.client.post(
            "/purchasePlaces", {
                "competition": competition["name"],
                "club": club["name"],
                "places": "1"
            }
        )
