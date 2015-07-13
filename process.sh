echo "Create database"
dropdb --if-exists nola_demographics
createdb nola_demographics
psql nola_demographics -c "CREATE EXTENSION postgis;"
psql nola_demographics -c "CREATE EXTENSION postgis_topology"
psql nola_demographics -c "SELECT postgis_full_version()"

echo "Import ACS data"
./import.py

echo "Import geo data"
PGCLIENTENCODING=LATIN1 ogr2ogr -f PostgreSQL PG:dbname=nola_demographics data/gz_2010_22_140_00_500k/gz_2010_22_140_00_500k.shp  -t_srs EPSG:900913 -nlt multipolygon -nln la_census_tracts

echo "Make some dots"
./dots.py
