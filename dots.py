#!/usr/bin/env python

import dataset
import os

from englewood import DotDensityPlotter
from functools import partial
from summarize import METRO_FIPS

DOT_DIVISOR = 5

POSTGRES_URL = 'postgresql:///nola_demographics'
db = dataset.connect(POSTGRES_URL)
census_table = db['census_data']


def get_2000_data(feature):
    #if feature.county in METRO_FIPS:
    if True:
        geoid = '{0}{1}{2}{3}'.format(feature.state, feature.county, feature.tract, feature.blkgroup)
        result = census_table.find_one(geo_id2=geoid, product='decennial-2000-bg')
        if result:
            print 'result for %s' % geoid
            return {
                'white': int(result['vd03']),
                'black': int(result['vd04']),
                'asian': int(result['vd06']),
                'hispanic': int(result['vd10']),
            }
        else:
            print 'no result for %s' % geoid


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


def get_2013_data(feature):
    #if feature.countyfp in METRO_FIPS:
    if True:
        result = census_table.find_one(geo_id2=feature.geoid, product='acs-2013-bg')
        return {
            'white': int(result['hd01_vd03']),
            'black': int(result['hd01_vd04']),
            'asian': int(result['hd01_vd06']),
            'hispanic': int(result['hd01_vd12']),
        }


def make_2013_dots():
    print 'making 2013 ACS block group dots'
    args = [
        'PG:dbname=nola_demographics host=localhost',
        'block_groups_2013',
        'ESRI Shapefile',
        'output/dots-2013',
        'dots-2013',
        get_2013_data,
        DOT_DIVISOR
    ]
    dots = DotDensityPlotter(*args)
    dots.plot()


if __name__ == '__main__':
    make_2000_dots()
    make_2013_dots()
