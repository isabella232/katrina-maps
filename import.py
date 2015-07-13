#!/usr/bin/env python

import dataset
import csv
from slugify import slugify
from collections import OrderedDict

INPUT_FILES = (
    ('acs-2013', 'data/acs2013_5yr_B02001_14000US22071014400/acs2013_5yr_B02001_14000US22071014400.csv'),
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

    data = []
    for i, row in enumerate(rows):
        processed_row = OrderedDict(zip(columns, row))
        processed_row['product'] = product
        processed_row['geographic_id'] = processed_row['geoid']
        del processed_row['geoid']

    table = db['census_data']
    table.insert_many(data)


if __name__ == '__main__':
    for product, filename in INPUT_FILES:
        import_data(db, product, filename)
