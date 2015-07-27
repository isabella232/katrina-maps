#!/usr/bin/env python

import dataset
import csv
from slugify import slugify
from collections import OrderedDict
from summarize import METRO_PARISHES

INPUT_FILES = (
    ('decennial-2000-bg', 'data/decennial-2000-bg/DEC_00_SF1_P004_with_ann.csv'),
    ('acs-2013-bg', 'data/acs-2013-bg/ACS_13_5YR_B03002_with_ann.csv'),
)
FIPS_CROSSWALK_FILE = 'data/fips-crosswalk/st22_la_cou.txt'
ESTIMATES_2000_FILE = 'data/populations-estimates/CO-EST00INT-SEXRACEHISP.csv.txt'

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

    table = db['census_data']

    data = []
    for i, row in enumerate(rows):
        processed_row = OrderedDict(zip(columns, row))
        processed_row['product'] = product
        data.append(processed_row)

    table.insert_many(data)


def import_fips():
    table = db['fips']

    with open(FIPS_CROSSWALK_FILE) as f:
        rows = list(csv.reader(f))

    columns = ['state', 'state_fp', 'county_fp', 'county_name', 'class_fp']

    data = []
    for row in rows:
        processed_row = OrderedDict(zip(columns, row))
        data.append(processed_row)

    table.insert_many(data)

def _write_2000_population_estimate(race, row):
    table = db['population_estimates']

    print 'processing %s (%s)' % (row['CTYNAME'], race)

    for year in range(2000, 2011):
        estimate_key = 'POPESTIMATE%s' % year

        data = {
            'county': row['CTYNAME'],
            'year': year,
        }
        data[race] = row[estimate_key]

        table.upsert(data, ['year', 'county'])


def import_2000_population_estimates():
    with open(ESTIMATES_2000_FILE) as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        if (row['STNAME'] == 'Louisiana'
                and row['CTYNAME'] in METRO_PARISHES
                and row['SEX'] == '0'):

            if row['ORIGIN'] == '2' and row['RACE'] == '0':
                _write_2000_population_estimate('hispanic', row)

            if row['ORIGIN'] == '1' and row['RACE'] == '1':
                _write_2000_population_estimate('white', row)

            if row['ORIGIN'] == '1' and row['RACE'] == '2':
                _write_2000_population_estimate('black', row)

            if row['ORIGIN'] == '1' and row['RACE'] == '3':
                _write_2000_population_estimate('american_indian', row)

            if row['ORIGIN'] == '1' and row['RACE'] == '4':
                _write_2000_population_estimate('asian', row)

            if row['ORIGIN'] == '1' and row['RACE'] == '5':
                _write_2000_population_estimate('native_hawaiian', row)

            if row['ORIGIN'] == '1' and row['RACE'] == '6':
                _write_2000_population_estimate('two_or_more', row)

            if row['ORIGIN'] == '0' and row['RACE'] == '0':
                _write_2000_population_estimate('total', row)

if __name__ == '__main__':
    import_2000_population_estimates()

    print 'import fips crosswalk'
    import_fips()

    for product, filename in INPUT_FILES:
        print 'processing %s' % product
        import_data(db, product, filename)

        
