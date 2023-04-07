# %%
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from dateutil import parser, tz
from datetime import datetime, timedelta
import ics

URL = "https://hugohouse.org/programs-events/"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
events_html = soup.find_all("div", class_="event")

@dataclass
class Event:
    title: str
    url: str
    content: str
    start: str
    end: str
    
def parse_hugo_event(event_html : str)->Event:
    title = event_html.find("h2", class_="entry-title").text
    url = event_html.find("h2", class_="entry-title").find("a").get("href")
    content = event_html.find('div', class_='entry-content').text.strip()
    raw_date = event_html.find('div', class_='entry-meta').text.replace('\t','').replace('\n','')
    date = datetime.strptime(raw_date.split(" at ")[0], "%B %d").replace(year=datetime.now().year)
    start = datetime.strptime(raw_date.split(" at ")[1].split(" - ")[0], "%I:%M%p").replace(year=date.year, month=date.month, day=date.day).astimezone(tz.tzlocal())
    end = datetime.strptime(raw_date.split(" at ")[1].split(" - ")[1][:-2], "%I:%M%p").replace(year=date.year, month=date.month, day=date.day).astimezone(tz.tzlocal())
    
    return Event(title, url, content, start.isoformat(), end.isoformat())

hugo_events = [parse_hugo_event(e) for e in events_html]

# %%
def add_hugo_event(hugo, calendar : ics.Calendar):
    event = ics.Event()
    event.name = hugo.title
    event.description = hugo.content
    event.begin = datetime.fromisoformat(hugo.start)
    event.end = datetime.fromisoformat(hugo.end)
    calendar.events.add(event)

# %%
hugo_ics = ics.Calendar()

[add_hugo_event(course, hugo_ics) for course in hugo_events]

with open("my.ics", "w") as f:
    f.write(hugo_ics.serialize())


