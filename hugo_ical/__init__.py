import logging

import azure.functions as func

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
# from zoneinfo import ZoneInfo
from dateutil import tz
from datetime import datetime
import ics

URL = "https://hugohouse.org/programs-events/"

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
    start = datetime.strptime(raw_date.split(" at ")[1].split(" - ")[0], "%I:%M%p").replace(year=date.year, month=date.month, day=date.day, tzinfo=tz.gettz("America/Los_Angeles"))
    end = datetime.strptime(raw_date.split(" at ")[1].split(" - ")[1][:-2], "%I:%M%p").replace(year=date.year, month=date.month, day=date.day, tzinfo=tz.gettz("America/Los_Angeles"))
    
    return Event(title, url, content, start.isoformat(), end.isoformat())

def add_hugo_event(hugo, calendar : ics.Calendar):
    event = ics.Event()
    event.name = hugo.title
    event.description = hugo.content
    event.begin = datetime.fromisoformat(hugo.start)
    event.end = datetime.fromisoformat(hugo.end)
    calendar.events.add(event)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    events_html = soup.find_all("div", class_="event")
    hugo_events = [parse_hugo_event(e) for e in events_html]
    
    hugo_ics = ics.Calendar()
    for course in hugo_events:
        add_hugo_event(course, hugo_ics)
    # with open("my.ics", "w") as f:
    #     f.write(hugo_ics.serialize())

    # name = req.params.get('name')
    # if not name:
    #     try:
    #         req_body = req.get_json()
    #     except ValueError:
    #         pass
    #     else:
    #         name = req_body.get('name')

    # if name:
    #     return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    # else:
    return func.HttpResponse(
        hugo_ics.serialize(),
        status_code=200,
        mimetype="text/calendar"
        
    )
    # var result = new HttpResponseMessage(HttpStatusCode.OK)
    # {
    #     Content = new ByteArrayContent(bytesCalendar)
    # };

    # result.Content.Headers.ContentDisposition =
    #     new System.Net.Http.Headers.ContentDispositionHeaderValue("attachment")
    # {
    #     FileName = "webinarinvite.ics"
    # };

    # result.Content.Headers.ContentType = new MediaTypeHeaderValue("application/octet-stream");

    # return resul