#!/usr/bin/env python

import dataset
import csv
from slugify import slugify
from collections import OrderedDict
from summarize import METRO_PARISHES, METRO_FIPS

INPUT_FILES = (
    ('decennial-2000-bg', 'data/decennial-2000-bg/DEC_00_SF1_P004_with_ann.csv'),
    ('decennial-2010-bg', 'data/decennial-2010-bg/DEC_10_SF1_P5_with_ann.csv'),
)
FIPS_CROSSWALK_FILE = 'data/fips-crosswalk/st22_la_cou.txt'
ESTIMATES_2000_FILE = 'data/populations-estimates/2000-2010/CO-EST00INT-SEXRACEHISP.csv.txt'
ESTIMATES_2010_FILE = 'data/populations-estimates/PEP_2014_PEPSR6H/PEP_2014_PEPSR6H_with_ann.csv'


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

def import_2010_population_estimates():
    table = db['population_estimates']

    with open(ESTIMATES_2010_FILE) as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        county_name, state = row['GEO.display-label'].split(', ')
        est_type = row['Year.id'][:4]
        est_year = row['Year.id'][4:]

        data = {
            'county': county_name,
            'year': est_year,
        }

        if (county_name in METRO_PARISHES
                and est_type == 'est7'
                and est_year != '2010'
                and row['Sex.id'] == 'totsex'):

            if row['Hisp.id'] == 'hisp':
                data['hispanic'] = row['totpop']

            if row['Hisp.id'] == 'nhisp':
                data['white'] = row['wa']
                data['black'] = row['ba']
                data['asian'] = row['aa']
                data['american_indian'] = row['ia']
                data['native_hawaiian'] = row['na']
                data['two_or_more'] = row['tom']

            if row['Hisp.id'] == 'tothisp':
                data['total'] = row['totpop']

            table.upsert(data, ['year', 'county'])

def fix_2000_geoids():
    block_group_table = db['block_groups_2000']
    for row in block_group_table.all():
        geoid_root = '{0}{1}{2}'.format(row['state'], row['county'], row['tract'])

        zero_pad = 12 - len(geoid_root)
        if zero_pad == 1:
            geoid = '{0}{1}'.format(geoid_root, row['blkgroup'])
        if zero_pad == 2:
            geoid = '{0}{1:02d}'.format(geoid_root, int(row['blkgroup']))
        if zero_pad == 3:
            geoid = '{0}{1:03d}'.format(geoid_root, int(row['blkgroup']))

        block_group_table.update({
            'ogc_fid': row['ogc_fid'],
            'geoid2': geoid,
        }, ['ogc_fid'])


if __name__ == '__main__':
    fix_2000_geoids()

    import_2000_population_estimates()
    import_2010_population_estimates()

    print 'import fips crosswalk'
    import_fips()

    for product, filename in INPUT_FILES:
        print 'processing %s' % product
        import_data(db, product, filename)
