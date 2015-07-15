#!/usr/bin/env python

import dataset
import os

from englewood import DotDensityPlotter
from functools import partial

DOT_DIVISOR = 25

POSTGRES_URL = 'postgresql:///nola_demographics'
db = dataset.connect(POSTGRES_URL)
census_table = db['census_data']


def get_2000_data(feature):
    result = census_table.find_one(geo_id2=feature.ctidfp00, product='decennial-2000')
    return {
        'white': int(result['vd03']),
        'black': int(result['vd04']),
        'asian': int(result['vd06']),
        'hispanic': int(result['vd10']),
    }


def make_2000_dots():
    print 'making 2000 decennial dots'
    args = [
        'PG:dbname=nola_demographics host=localhost',
        'census_geography_2000',
        'ESRI Shapefile',
        'output/dots-decennial-2000',
        'dots-decennial-2000',
        get_2000_data,
        DOT_DIVISOR
    ]
    dots = DotDensityPlotter(*args)
    dots.plot()


def get_2010_data(feature):
    result = census_table.find_one(geo_id=feature.geo_id, product='decennial-2010')
    return {
        'white': int(result['d003']),
        'black': int(result['d004']),
        'asian': int(result['d006']),
        'hispanic': int(result['d010']),
    }


def make_2010_dots():
    print 'making 2010 decennial dots'
    args = [
        'PG:dbname=nola_demographics host=localhost',
        'census_geography_2010',
        'ESRI Shapefile',
        'output/dots-decennial-2010',
        'dots-decennial-2010',
        get_2010_data,
        DOT_DIVISOR
    ]
    dots = DotDensityPlotter(*args)
    dots.plot()


def get_acs_data(feature, product):
    result = census_table.find_one(geo_id=feature.geo_id, product=product)
    if result:
        return {
            'white': int(result['hd01_vd03']),
            'black': int(result['hd01_vd04']),
            'asian': int(result['hd01_vd06']),
            'hispanic': int(result['hd01_vd12']),
        }
    else:
        print 'warning: no data for %s %s' % (feature.geo_id, product)

def make_acs_dots(year):
    print 'making %s acs dots' % year
    output_dir = 'output/dots-acs-%s' % year
    try:
        os.makedirs(output_dir)
    except OSError:
        pass

    args = [
        'PG:dbname=nola_demographics host=localhost',
        'census_geography_2010',
        'ESRI Shapefile',
        output_dir,
        'dots-acs-%s' % year,
        partial(get_acs_data, product='acs-%s' % year),
        DOT_DIVISOR
    ]
    dots = DotDensityPlotter(*args)
    dots.plot()



if __name__ == '__main__':
    make_2000_dots()
    make_2010_dots()
    for year in range(2009, 2014):
        make_acs_dots(year)
