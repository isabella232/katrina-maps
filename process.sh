echo "Create database"
dropdb --if-exists nola_demographics
createdb nola_demographics
psql nola_demographics -c "CREATE EXTENSION postgis;"
psql nola_demographics -c "CREATE EXTENSION postgis_topology"
psql nola_demographics -c "SELECT postgis_full_version()"

# bbox for seven parish region, roughly:
# -90.71961042991820534 28.83132805149813294, -86.59184855829140304 30.7471360415180115
# -90.71961042991820534,28.83132805149813294,-86.59184855829140304,30.7471360415180115 

# Memorialized for now
# mkdir data/bg22_d00_shp-clean
# mapshaper data/bg22_d00_shp/bg22_d00.shp -clip bbox=-90.71961042991820534,28.83132805149813294,-86.59184855829140304,30.7471360415180115 -erase data/lousiana-water/tiger_la_water_CENSUS_2006.shp -simplify 30% -o data/bg22_d00_shp-clean/bg22_d00_shp-clean.shp

# mkdir data/cb_2013_22_bg_500k-clean/
# mapshaper data/cb_2013_22_bg_500k/cb_2013_22_bg_500k.shp -clip bbox=-90.71961042991820534,28.83132805149813294,-86.59184855829140304,30.7471360415180115 -erase data/lousiana-water/tiger_la_water_CENSUS_2006.shp -simplify 30% -o data/cb_2013_22_bg_500k-clean/cb_2013_22_bg_500k-clean.shp

# mkdir Parishes_LDOTD_2007-clean
# mapshaper data/Parishes_LDOTD_2007/Parishes_LDOTD_2007.shp -clip bbox=-90.71961042991820534,28.83132805149813294,-86.59184855829140304,30.7471360415180115 -erase data/lousiana-water/tiger_la_water_CENSUS_2006.shp -simplify 30% -o data/Parishes_LDOTD_2007-clean/Parishes_LDOTD_2007-clean.shp
# mapshaper data/Parishes_LDOTD_2007/Parishes_LDOTD_2007.shp -erase data/lousiana-water/tiger_la_water_CENSUS_2006.shp -simplify 30% -o data/Parishes_LDOTD_2007-clean/Parishes_LDOTD_2007-clean.shp


#rm -Rf ./output/*

echo "Import 2000 census block groups"
PGCLIENTENCODING=LATIN1 ogr2ogr -f PostgreSQL PG:dbname=nola_demographics data/bg22_d00_shp-clean/bg22_d00_shp-clean.shp -s_srs EPSG:4269  -t_srs EPSG:4269 -nlt multipolygon -nln block_groups_2000

echo "Import 2013 census block groups"
PGCLIENTENCODING=LATIN1 ogr2ogr -f PostgreSQL PG:dbname=nola_demographics data/cb_2013_22_bg_500k-clean/cb_2013_22_bg_500k-clean.shp  -t_srs EPSG:4269 -nlt multipolygon -nln block_groups_2013

echo "Import census data"
./import.py

psql nola_demographics -c "create or replace view census_2000_race as 
select bg.wkb_geometry, bg.geoid2, d.vd05 as white, d.vd06 as black, d.vd08 as asian, d.vd02 as hispanic
from block_groups_2000 bg
join census_data d on bg.geoid2 = d.geo_id2
where d.product='decennial-2000-bg';"

echo "Generate summary files"
./summarize.py

echo "Make some dots"
./dots.py
