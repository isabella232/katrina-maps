#!/usr/bin/env python

import dataset
import csv
from slugify import slugify
from collections import OrderedDict

INPUT_FILES = (
    ('decennial-2000', 'data/decennial-2000/DEC_00_SF1_P008_with_ann.csv'),
    ('decennial-2010', 'data/decennial-2010/DEC_10_SF1_P5_with_ann.csv'),
    ('acs-2013', 'data/acs-2013/ACS_13_5YR_B03002_with_ann.csv'),
    ('acs-2012', 'data/acs-2012/ACS_12_5YR_B03002_with_ann.csv'),
    ('acs-2011', 'data/acs-2011/ACS_11_5YR_B03002_with_ann.csv'),
    ('acs-2010', 'data/acs-2010/ACS_10_5YR_B03002_with_ann.csv'),
    ('acs-2009', 'data/acs-2009/ACS_09_5YR_B03002_with_ann.csv'),
)

POSTGRES_URL = 'postgresql:///nola_demographics'
db = dataset.connect(POSTGRES_URL)


def import_data(db, product, filename):
    """
    Process and read in data
    """
    with open(filename) as f:
        rows = list(csv.reader(f))

    raw_columns = rows.pop(0)

    columns = [slugify(column, separator='_') for column in raw_columns]
    #for column in raw_columns:
        #processed_name = .replace('some_other_race', 'other')
        #name_parts = processed_name.split('_')
        #if len(name_parts) > 1:
            #processed_name = '_'.join(name_parts[1:])
        #columns.append(processed_name)

    table = db['census_data']

    data = []
    for i, row in enumerate(rows):
        processed_row = OrderedDict(zip(columns, row))
        processed_row['product'] = product
        data.append(processed_row)

    table.insert_many(data)


if __name__ == '__main__':
    for product, filename in INPUT_FILES:
        print 'processing %s' % product
        import_data(db, product, filename)
