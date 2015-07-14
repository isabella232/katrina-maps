#!/usr/bin/env python

import dataset

from englewood import DotDensityPlotter

POSTGRES_URL = 'postgresql:///nola_demographics'
db = dataset.connect(POSTGRES_URL)
census_table = db['census_data']

def get_data(feature):
    result = census_table.find_one(geo_id=feature.geo_id)
    return {
        'white': int(result['d003']),
        'black': int(result['d004']),
        'asian': int(result['d006']),
        #'hispanic': result['d010'],
    }

def make_dots():
    args = [
        'PG:dbname=nola_demographics host=localhost',
        'la_census_tracts',
        'ESRI Shapefile',
        'output',
        'dots',
        get_data,
        25
    ]
    dots = DotDensityPlotter(*args)
    dots.plot()

if __name__ == '__main__':
    make_dots()
