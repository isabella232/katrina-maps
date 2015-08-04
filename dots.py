#!/usr/bin/env python

import dataset
import os

from englewood import DotDensityPlotter
from functools import partial
from summarize import METRO_FIPS

import locale
locale.setlocale(locale.LC_ALL, 'en_US')

DOT_DIVISOR = 5

POSTGRES_URL = 'postgresql:///nola_demographics'
db = dataset.connect(POSTGRES_URL)
census_table = db['census_data']


def get_2000_data(feature):
    if feature.county in METRO_FIPS:
        result = census_table.find_one(geo_id2=feature.geoid2, product='decennial-2000-bg')
        if result:
            print 'found %s' % feature.geoid2
            return {
                'white': int(result['vd05']),
                'black': int(result['vd06']),
                'asian': int(result['vd08']),
                'hispanic': int(result['vd02']),
            }


def make_2000_dots():
    print 'making 2000 decennial dots'
    args = [
        'PG:dbname=nola_demographics host=localhost',
        'block_groups_2000',
        'ESRI Shapefile',
        'output/dots-2000',
        'dots-2000',
        get_2000_data,
        DOT_DIVISOR
    ]
    dots = DotDensityPlotter(*args)
    dots.plot()


def get_2010_data(feature):
    if feature.county in METRO_FIPS:
        result = census_table.find_one(geo_id=feature.geo_id, product='decennial-2010-bg')
        return {
            'white': int(result['d003']),
            'black': int(result['d004']),
            'asian': int(result['d006']),
            'hispanic': int(result['d010']),
        }


def make_2010_dots():
    print 'making 2010 decennial block group dots'
    args = [
        'PG:dbname=nola_demographics host=localhost',
        'block_groups_2010',
        'ESRI Shapefile',
        'output/dots-2010',
        'dots-2010',
        get_2010_data,
        DOT_DIVISOR
    ]
    dots = DotDensityPlotter(*args)
    dots.plot()


def get_household_dot_data(year, feature):
    table = db['household_mail']
    result = table.find_one(neighborhood=feature.gnocdc_lab, year=str(year))
    if result:
        return {
            'total': result['households_change'],
        }
    else:
        print 'no result for %s' % feature.lup_lab

def make_household_dots(year):
    try:
        os.makedirs('output/household-dots-%s' % year)
    except OSError:
        pass

    get_data = partial(get_household_dot_data, year)
    args = [
        'PG:dbname=nola_demographics host=localhost',
        'nola_neighborhoods',
        'ESRI Shapefile',
        'output/household-dots-%s' % year,
        'household-dots-%s' % year,
        get_data,
        1
    ]
    dots = DotDensityPlotter(*args)
    dots.plot()


if __name__ == '__main__':
    make_2000_dots()
    make_2010_dots()
    #for year in range(2005, 2015, 3):
        #make_household_dots(year)
