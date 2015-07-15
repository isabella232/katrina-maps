echo "Create database"
dropdb --if-exists nola_demographics
createdb nola_demographics
psql nola_demographics -c "CREATE EXTENSION postgis;"
psql nola_demographics -c "CREATE EXTENSION postgis_topology"
psql nola_demographics -c "SELECT postgis_full_version()"

echo "Import census data"
./import.py

echo "Import 2000 census tracts"
PGCLIENTENCODING=LATIN1 ogr2ogr -f PostgreSQL PG:dbname=nola_demographics data/tl_2010_22_tract00/tl_2010_22_tract00.shp  -t_srs EPSG:4269 -nlt multipolygon -nln census_geography_2000

echo "Import 2010 census tracts"
PGCLIENTENCODING=LATIN1 ogr2ogr -f PostgreSQL PG:dbname=nola_demographics data/gz_2010_22_140_00_500k/gz_2010_22_140_00_500k.shp  -t_srs EPSG:4269 -nlt multipolygon -nln census_geography_2010

echo "Make some dots"
./dots.py
