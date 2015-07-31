#!/usr/bin/env python
from slugify import slugify

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
METRO_FIPS = [
    '051',
    '071',
    '075',
    '087',
    '103',
    '089',
    '095',
]
LOWER_NINTH_BLOCKGROUPS = [
    '1500000US220710007011',
    '1500000US220710007012',
    '1500000US220710007013',
    '1500000US220710007014',
    '1500000US220710009011',
    '1500000US220710009012',
    '1500000US220710009013',
    '1500000US220710009014',
    '1500000US220710009021',
    '1500000US220710009022',
    '1500000US220710009023',
    '1500000US220710009024',
    '1500000US220710009031',
    '1500000US220710009032',
    '1500000US220710009033',
    '1500000US220710009034',
    '1500000US220710009041',
    '1500000US220710009042',
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
            (sum(c.vd03::float)/sum(c.vd01::float)) as white_percent,
            sum(c.vd04::integer) as black,
            (sum(c.vd04::float)/sum(c.vd01::float)) as black_percent,
            sum(c.vd06::integer) as asian,
            (sum(c.vd06::float)/sum(c.vd01::float)) as asian_percent,
            sum(c.vd10::integer) as hispanic,
            (sum(c.vd10::float)/sum(c.vd01::float)) as hispanic_percent
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
            (sum(c.d003::float)/sum(c.d001::float)) as white_percent,
            sum(c.d004::integer) as black,
            (sum(c.d004::float)/sum(c.d001::float)) as black_percent,
            sum(c.d006::integer) as asian,
            (sum(c.d006::float)/sum(c.d001::float)) as asian_percent,
            sum(c.d010::integer) as hispanic,
            (sum(c.d010::float)/sum(c.d001::float)) as hispanic_percent
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
            (sum(c.hd01_vd03::float)/sum(c.hd01_vd01::float)) as white_percent,
            sum(c.hd01_vd04::integer) as black,
            (sum(c.hd01_vd04::float)/sum(c.hd01_vd01::float)) as black_percent,
            sum(c.hd01_vd06::integer) as asian,
            (sum(c.hd01_vd06::float)/sum(c.hd01_vd01::float)) as asian_percent,
            sum(c.hd01_vd12::integer) as hispanic,
            (sum(c.hd01_vd12::float)/sum(c.hd01_vd01::float)) as hispanic_percent
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

def summarize_population_estimates():

    for county in METRO_PARISHES:
        filename = 'output/population-summary/{0}.csv'.format(slugify(county))
        result = db.query(""" 
            select 
                year,
                total,
                white,
                black,
                hispanic,
                asian,
                american_indian,
                native_hawaiian,
                two_or_more
            from
                population_estimates
            where
                county='{0}' 
            order by year
            

        """.format(county))
        dataset.freeze(result, format='csv', filename=filename)

def summarize_lower_ninth():
    blockgroup_list = ["'{0}'".format(geoid) for geoid in LOWER_NINTH_BLOCKGROUPS]
    blockgroups = ','.join(blockgroup_list)

    pop2000 = list(db.query("""
        select
            sum(c.vd01::integer) as total,
            sum(c.vd03::integer) as white,
            sum(c.vd04::integer) as black,
            sum(c.vd06::integer) as asian,
            sum(c.vd10::integer) as hispanic
        from census_data c
        where
            c.product='decennial-2000-bg' and
            c.geo_id in ({0})
    """.format(blockgroups)))[0]

    pop2010 = list(db.query("""
        select
            sum(c.d001::integer) as total,
            sum(c.d003::integer) as white,
            sum(c.d004::integer) as black,
            sum(c.d006::integer) as asian,
            sum(c.d010::integer) as hispanic
        from census_data c
        where
            c.product='decennial-2010-bg' and
            c.geo_id in ({0})
    """.format(blockgroups)))[0]

    pop2000['year'] = 2000
    pop2010['year'] = 2010
    data = [pop2000, pop2010]
    dataset.freeze(data, format='csv', filename='data/lower-ninth.csv')

if __name__ == '__main__':
    try:
        os.makedirs('output/population-summary/')
    except OSError:
        pass

    print 'summarize lower 9th'
    summarize_lower_ninth()

    print 'summarize_population_estimates'
    summarize_population_estimates()

