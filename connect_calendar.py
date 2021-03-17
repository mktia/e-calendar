# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import date, datetime
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Calendar:
    @staticmethod
    def get_events(in_date):
        # If modifying these scope, delete the file token.pickle
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        # 'Z' indicates UTC time
        time_min = f'{datetime(in_date.year, in_date.month, 1).isoformat()}Z'
        next_year = in_date.year if in_date.month < 12 else in_date.year + 1
        next_month = in_date.month + 1 if in_date.month != 12 else 1
        dt = datetime.fromtimestamp(
            datetime(next_year, next_month, 1).timestamp() - 60 * 60 * 9)
        time_max = f'{dt.isoformat()}Z'
        now = f'{in_date.isoformat()}T00:00:00.000Z'

        # get holidays in this month
        holidays_id = 'ja.japanese#holiday@group.v.calendar.google.com'
        res = service.events().list(
            calendarId=holidays_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        tmp = [[int(i) for i in r['start']['date'].split('-')]
               for r in res['items']]
        holidays_this_month = [int(date[2]) for date in tmp]

        res = service.calendarList().list().execute()
        calendars = [r['id'] for r in res['items']]
        calendars.remove(holidays_id)

        all_events = []
        events = []
        for calendar_id in calendars:
            # get all the events in this month
            res = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            all_events += res['items']
            # get the events from 'now'
            res = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events += res['items']
        # get the days having schedule in this month
        tmp = []
        for e in all_events:
            start = e['start']['date'] if 'date' in e['start'] else \
                e['start']['dateTime'].split('T')[0]
            tmp.append([int(i) for i in start.split('-')])
        events_this_month = [int(date[2]) for date in tmp]

        sorted_events = []
        for event in events:
            start = event['start']['dateTime'] if 'dateTime' in event['start'].keys() \
                else event['start']['date']
            sorted_events.append([event['summary'], start.split('T')])
        sorted_events = sorted(sorted_events, key=lambda x: x[1])

        return [
            sorted_events,
            events_this_month,
            holidays_this_month
        ]


if __name__ == '__main__':
    res = Calendar.get_events(date.today())
    print(res)
