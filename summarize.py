#!/usr/bin/env python

import dataset

POSTGRES_URL = 'postgresql:///nola_demographics'
db = dataset.connect(POSTGRES_URL)

def summarize_2010():
    results = db.query("""
        select 
            sum(d003::integer) as white, 
            sum(d004::integer) as black,
            sum(d006::integer) as asian,
            sum(d010::integer) as hispanic
        from census_data
        where 
            product='decennial-2010' and
            geo_display_label like '%Orleans Parish%'
        
    """)
    for result in results: 
        print result

if __name__ == '__main__':
    summarize_2010()
