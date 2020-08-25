#!/usr/bin/env python3

import datetime
import sys

import numpy
import yaml

import matplotlib
matplotlib.use('cairo')
import matplotlib.pyplot as plt

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as yfile:
        covid_data = yaml.load(yfile, Loader=yaml.SafeLoader)

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

    times = numpy.array(times)
    fig, ax = plt.subplots(2, 2, constrained_layout=True)

    day_width = 86400
    ax[0,0].bar(times[1:] + day_width/2, new_cases[1:], width=day_width)
    tick_labels = [d.strftime('%Y-%m-%d') for d in dates]
    ax[0,0].set_xticks(times[1:])
    ax[0,0].set_xticklabels(
        tick_labels[1:], rotation=-45, ha='left', rotation_mode='anchor')
    ax[0,0].set_ylabel('new cases')

    ax[0,1].step(times, numpy.cumsum(new_cases))
    ax[0,1].set_ylabel('total cases')
    ax[0,1].set_xticks(times[1:])
    ax[0,1].set_xticklabels(
        tick_labels[1:], rotation=-45, ha='left', rotation_mode='anchor')
    ax[0,1].grid()

    ax[1,0].bar(times[1:] + day_width/2, new_tests[1:], width=day_width)
    tick_labels = [d.strftime('%Y-%m-%d') for d in dates]
    ax[1,0].set_xticks(times[1:])
    ax[1,0].set_xticklabels(
        tick_labels[1:], rotation=-45, ha='left', rotation_mode='anchor')
    ax[1,0].set_ylabel('new tests')

    ax[1,1].step(times, numpy.cumsum(new_tests))
    ax[1,1].set_ylabel('total tests')
    ax[1,1].set_xticks(times[1:])
    ax[1,1].set_xticklabels(
        tick_labels[1:], rotation=-45, ha='left', rotation_mode='anchor')
    ax[1,1].grid()

    fig.savefig('covid_stats.png', format='png')
