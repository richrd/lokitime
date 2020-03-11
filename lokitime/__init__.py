#!/usr/bin/env python3

from datetime import date, datetime, timedelta
import requests
from bs4 import BeautifulSoup


class LokitimeApiError(Exception):
    pass


class LokitimeAPI(object):
    def __init__(self):
        self.api_root = "https://www.lokitime.com/kiinteisto/"
        self.session = requests.Session()

    def login(self, username, password):
        """Start the session by logging in."""
        data = {
            "user_name": username,
            "password": password
        }

        response = self.session.post(
            self.api_root + "admin/login/doLogin",
            data=data,
        )

        if "Väärä käyttäjätunnus tai salasana" in response.text:
            # "Incorrect username or password"
            raise LokitimeApiError("Invalid credentials.")
        return True

    def get_calendars(self):
        """Get a list of available calendars."""
        response = self.session.get(
            self.api_root + "fi/resident/reservation_calendars"
        )
        page = BeautifulSoup(response.text, "html.parser")

        # Find the calendar select options
        options = page.find("div", {
            "class": "reservation-groups"
        }).find("select").find_all("option")

        # Map the elements into a convenient list of dicts
        calendars = list(map(lambda opt: {
            "id": opt.get("value"),
            "name": opt.text,
        }, options))

        return calendars

    def get_calendar_range(self, id, start_date, end_date):
        """Get calendar reservations within a date range."""
        data = {
            "calendar_id": id,
            "start_date": start_date,
            "end_date": end_date,
        }

        response = self.session.post(
            self.api_root + "fi/resident/get_calendar_reservations",
            data=data,
        )

        if response.status_code == 404:
            raise LokitimeApiError("Calendar not found or not logged in.")
        return response.json()

    def get_calendar_today(self, id):
        """Get todays calendar reservations."""
        today = date.today()
        return self.get_calendar_range(id, today, today)

    def get_calendar_this_week(self, id):
        """Get this weeks calendar reservations."""
        today = datetime.now().date()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return self.get_calendar_range(id, start.isoformat(), end.isoformat())
