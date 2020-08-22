#!/usr/bin/env python3

import datetime
import sys

import numpy
import yaml

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as yfile:
        covid_data = yaml.load(yfile)

    total_cases = []
    new_cases = []
    total_tests = []
    new_tests = []
    dates = []
    times = []

    for date, data in covid_data.items():
        this_day = datetime.datetime.strptime(date, '%Y-%m-%d')
        dates.append(this_day)
        times.append(this_day.timestamp())

        if 'daily_cases' in data:
            new_cases.append(data['daily_cases'])
        else:
            new_cases.append(data['period_cases'])
        if 'daily_tests' in data:
            new_tests.append(data['daily_tests'])
        else:
            new_tests.append(data['period_tests'])

    f_new_cases =  plt.figure()
    plt.bar(times[1:], new_cases[1:])
    tick_labels = [d.strftime('%Y-%m-%d') for d in dates]
    plt.xticks(times[1:], tick_labels[1:])
    plt.ylabel('new cases')

    f_total_cases = plt.figure()
    plt.step(times, numpy.cumsum(new_cases))
    plt.ylabel('total cases')
    plt.xticks(times, tick_labels)
    plt.grid()

    f_new_cases.savefig('new_cases')
    f_total_cases.savefig('total_cases')
