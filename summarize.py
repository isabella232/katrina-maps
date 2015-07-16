#!/usr/bin/env python

import dataset
import os

METRO_PARISHES = [
    'Jefferson Parish',
    'Orleans Parish',
    'Plaquemines Parish',
    'St. Bernard Parish',
    'St. Tammany Parish',
    'St. Charles Parish',
    'St. John the Baptist Parish',
]

POSTGRES_URL = 'postgresql:///nola_demographics'
db = dataset.connect(POSTGRES_URL)


def get_parishes():
    parish_list = ["'{0}'".format(parish) for parish in METRO_PARISHES]
    return ', '.join(parish_list)


def summarize_2000():
    result = db.query("""
        select
            f.county_name,
            sum(c.vd01::integer) as total,
            sum(c.vd03::integer) as white,
            sum(c.vd04::integer) as black,
            sum(c.vd06::integer) as asian,
            sum(c.vd10::integer) as hispanic
        from census_data c
        join census_geography_2000 g on
            c.geo_id2 = g.ctidfp00
        join fips f on
            g.countyfp00 = f.county_fp
        where
            c.product='decennial-2000' and
            f.county_name in ({0})
        group by
            f.county_name
    """.format(get_parishes()))

    dataset.freeze(result, format='csv', filename='output/population-summary/decennial-population-2000.csv')


def summarize_2010():
    result = db.query("""
        select
            f.county_name,
            sum(c.d001::integer) as total,
            sum(c.d003::integer) as white,
            sum(c.d004::integer) as black,
            sum(c.d006::integer) as asian,
            sum(c.d010::integer) as hispanic
        from census_data c
        join census_geography_2010 g on
            c.geo_id = g.geo_id
        join fips f on
            g.county = f.county_fp
        where
            c.product='decennial-2010' and
            f.county_name in ({0})

        group by
            f.county_name
    """.format(get_parishes()))

    dataset.freeze(result, format='csv', filename='output/population-summary/decennial-population-2010.csv')


def summarize_acs(year):
    result = db.query("""
        select
            f.county_name,
            sum(c.hd01_vd01::integer) as total,
            sum(c.hd01_vd03::integer) as white,
            sum(c.hd01_vd04::integer) as black,
            sum(c.hd01_vd06::integer) as asian,
            sum(c.hd01_vd12::integer) as hispanic
        from census_data c
        join census_geography_2010 g on
            c.geo_id = g.geo_id
        join fips f on
            g.county = f.county_fp
        where
            c.product='acs-{0}' and
            f.county_name in ({1})
        group by
            f.county_name
    """.format(year, get_parishes()))

    dataset.freeze(result, format='csv', filename='output/population-summary/acs-population-{0}.csv'.format(year))


if __name__ == '__main__':
    try:
        os.makedirs('output/population-summary/')
    except OSError:
        pass

    print 'summarizing decennial 2000'
    summarize_2000()

    print 'summarizing decennial 2010'
    summarize_2010()

    for year in range(2009, 2014):
        print 'summarizing acs {0}'.format(year)
        summarize_acs(year)
