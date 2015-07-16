#!/usr/bin/env python

import dataset

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

def summarize_2010():
    parish_list = ["'{0}'".format(parish) for parish in METRO_PARISHES]
    parishes = ', '.join(parish_list)

    result = db.query("""
        select
            f.county_name,
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
    """.format(parishes))

    dataset.freeze(result, format='csv', filename='output/population-2010.csv')

if __name__ == '__main__':
    print 'summarizing 2010'
    summarize_2010()
