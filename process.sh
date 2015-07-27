echo "Create database"
dropdb --if-exists nola_demographics
createdb nola_demographics
psql nola_demographics -c "CREATE EXTENSION postgis;"
psql nola_demographics -c "CREATE EXTENSION postgis_topology"
psql nola_demographics -c "SELECT postgis_full_version()"

rm -Rf ./output/*

echo "Import census data"
./import.py

echo "Import 2000 census block groups"
PGCLIENTENCODING=LATIN1 ogr2ogr -f PostgreSQL PG:dbname=nola_demographics data/bg22_d00_shp/bg22_d00.shp -s_srs EPSG:4269  -t_srs EPSG:4269 -nlt multipolygon -nln block_groups_2000

echo "Import 2013 census block groups"
PGCLIENTENCODING=LATIN1 ogr2ogr -f PostgreSQL PG:dbname=nola_demographics data/cb_2013_22_bg_500k/cb_2013_22_bg_500k.shp  -t_srs EPSG:4269 -nlt multipolygon -nln block_groups_2013


echo "Generate summary files"
./summarize.py

echo "Make some dots"
./dots.py
