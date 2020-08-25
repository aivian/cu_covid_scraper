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
    day_width = 86400

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
    dates.append(this_day + datetime.timedelta(days=1))
    times.append(dates[-1].timestamp())

    times = numpy.array(times)
    fig, ax = plt.subplots(2, 2, constrained_layout=True)

    ax[0,0].bar(times[:-1] + day_width/2, new_cases, width=day_width)
    tick_labels = [d.strftime('%Y-%m-%d') for d in dates]
    ax[0,0].set_xticks(times)
    ax[0,0].set_xticklabels(
        tick_labels, rotation=-45, ha='left', rotation_mode='anchor')
    ax[0,0].set_ylabel('new cases')

    ax[0,1].step(
        times + day_width,
        numpy.cumsum([0.0,] + new_cases),
        where='pre')
    ax[0,1].set_ylabel('total cases')
    ax[0,1].set_xticks(times[1:])
    ax[0,1].set_xticklabels(
        tick_labels[1:], rotation=-45, ha='left', rotation_mode='anchor')
    ax[0,1].grid()
    ax[0,1].set_ylim([0, numpy.sum(new_cases) * 1.1])

    ax[1,0].bar(times[:-1] + day_width/2, new_tests, width=day_width)
    tick_labels = [d.strftime('%Y-%m-%d') for d in dates]
    ax[1,0].set_xticks(times)
    ax[1,0].set_xticklabels(
        tick_labels, rotation=-45, ha='left', rotation_mode='anchor')
    ax[1,0].set_ylabel('new tests')

    ax[1,1].step(
        times + day_width,
        numpy.cumsum([0.0,] + new_tests),
        where='pre')
    ax[1,1].set_ylabel('total tests')
    ax[1,1].set_xticks(times[1:])
    ax[1,1].set_xticklabels(
        tick_labels[1:], rotation=-45, ha='left', rotation_mode='anchor')
    ax[1,1].grid()
    ax[1,1].set_ylim([0, numpy.sum(new_tests) * 1.1])

    fig.savefig('covid_stats.png', format='png')
