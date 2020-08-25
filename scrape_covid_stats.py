#!/usr/bin/env python3

import copy
import datetime
from html.parser import HTMLParser
import os
import re
import requests
import yaml

class DashboardParser(HTMLParser):
    def __init__(self):
        super(DashboardParser, self).__init__()

        self._mode = None
        self._tag_modes = {
            'tests': self._handle_tag_tests,
            'cases': self._handle_tag_cases,
            'util_rate': self._handle_tag_util,
            }
        self._data_modes = {
            'tests': self._handle_data_tests,
            'tests_dates': self._handle_data_tests_dates,
            'cases': self._handle_data_cases,
            'cases_dates': self._handle_data_cases_dates,
            'util_rate': self._handle_data_util,
            }

    def handle_starttag(self, tag, attrs):
        if self._mode in self._tag_modes:
            self._tag_modes[self._mode](tag, attrs)

    def handle_data(self, data):
        if self._mode in self._data_modes:
            self._data_modes[self._mode](data)

        if 'CU Boulder Testing' in data:
            self._mode = 'tests'
        if 'New cases' in data:
            self._mode = 'cases'
        if 'Utilization rate' in data:
            self._mode = 'util_rate'

    def _handle_tag_cases(self, tag, attrs):
        return

    def _handle_data_cases(self, data):
        if data == '\n':
            return
        self._n_cases = int(data)
        self._mode = 'cases_dates'

    def _handle_data_cases_dates(self, data):
        if data == '\n':
            return

        dates = self._parse_date_range(data)
        self._cases_start_date = dates[0]
        self._cases_end_date = dates[1]
        self._cases_dates = data

        self._mode = None

    def _handle_tag_tests(self, tag, attrs):
        return

    def _handle_data_tests(self, data):
        if data == '\n':
            return
        self._n_tests = int(data.replace(',', ''))
        self._mode = 'tests_dates'

    def _handle_data_tests_dates(self, data):
        if data == '\n':
            return

        dates = self._parse_date_range(data)
        self._tests_start_date = dates[0]
        self._tests_end_date = dates[1]
        self._report_date = dates[1] + datetime.timedelta(days=1)
        self._tests_dates = data

        self._mode = None

    def _handle_tag_util(self, tag, attrs):
        return

    def _handle_data_util(self, data):
        if data == '\n':
            return

        self._util_rate = float(data[:-1]) / 100.0
        self._mode = None

    def _parse_date_range(self, data):
        start_date, end_date = re.findall('([0-9]+/[0-9]+)+', data)

        start_month, start_day = start_date.split('/')
        start_month = int(start_month)
        start_day = int(start_day)

        end_month, end_day = end_date.split('/')
        end_month = int(end_month)
        end_day = int(end_day)

        end_year = datetime.datetime.now().year
        if end_month == 12 and start_month != end_month:
            start_year = end_year - 1
        else:
            start_year = end_year

        start_date = datetime.datetime(
            year=start_year, month=start_month, day=start_day)
        end_date = datetime.datetime(
            year=end_year, month=end_month, day=end_day)

        return start_date, end_date

    def save_data(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as yfile:
                current_data = yaml.load(yfile, Loader=yaml.SafeLoader)
        else:
            current_data = {}

        day_id = self._report_date.strftime('%Y-%m-%d')
        if day_id in current_data:
            return

        daily_data = {
            'period_start': self._tests_start_date.strftime('%Y-%m-%d'),
            'period_end': self._tests_end_date.strftime('%Y-%m-%d'),
            'period_cases': self._n_cases,
            'period_tests': self._n_tests,
            'period_util': self._util_rate,
            }


        start_day = self._tests_start_date# - datetime.timedelta(days=1)
        start_day_id = start_day.strftime('%Y-%m-%d')
        if start_day_id not in current_data:
            delta = datetime.timedelta(days=365)
            for day in current_data.keys():
                delta_day = (
                    start_day -
                    datetime.timedelta(days=1) -
                    datetime.datetime.strptime(day, '%Y-%m-%d'))
                if delta_day < delta and delta_day > 0:
                    delta = delta_day
                    start_day_id = copy.deepcopy(day)

        last_day = datetime.datetime.strptime('1900-01-01', '%Y-%m-%d')
        for day in current_data.keys():
            this_day = datetime.datetime.strptime(day, '%Y-%m-%d')
            if this_day > last_day:
                last_day = this_day
        last_day_id = last_day.strftime('%Y-%m-%d')

        daily_data['daily_cases'] = (
            daily_data['period_cases'] -
            current_data[last_day_id]['total_cases'] +
            current_data[start_day_id]['total_cases']
        )
        daily_data['daily_tests'] = (
            daily_data['period_tests'] -
            current_data[last_day_id]['total_tests'] +
            current_data[start_day_id]['total_tests']
        )

        daily_data['total_cases'] = (
            current_data[start_day_id]['total_cases'] +
            daily_data['period_cases'])
        daily_data['total_tests'] = (
            current_data[start_day_id]['total_tests'] +
            daily_data['period_tests'])

        current_data[day_id] = daily_data

        pdb.set_trace()
        with open(file_path, 'w') as yfile:
            yaml.dump(current_data, yfile)

if __name__ == '__main__':
    cu_dashboard_url = 'https://www.colorado.edu/covid-19-ready-dashboard'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Cache-Control': 'max-age=0',
        'Cookie': 'has_js=1; SESSION_LANGUAGE=eng',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'
        }
    r = requests.get(cu_dashboard_url, headers=headers)

    parser = DashboardParser()
    parser.feed(r.content.decode('utf-8'))

    parser.save_data('cu_dashboard_data.yaml')
