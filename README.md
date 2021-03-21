# NYC Taxi Ride Sharing

## Members
1. Benito Alvares
2. Harish Ventaktaraman
3. Karan venkatesh Davanam
4. Prajwal Kishor Kammardi

## Components needed

1. PostgreSQL installed
2. PostGIS extension installed in the relevant schema
3. Python 3.6
4. pip or conda virtual environments
5. Components specified in the `requirements.txt` or `conda_requirements.txt`


## PostgreSQL installation instructions

1. Have a Role called `nycrideshare` with password `nycrideshare` created in the environment. (You can also change the python file to specify the ID/Password of you environments)
2. Create a new database

```SQL
CREATE DATABASE nyc_taxi
    WITH
    OWNER = nycrideshare
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;
```

3. Create schema called as `nyc_taxi_schema` and `public` (if not present already)

```SQL
CREATE SCHEMA nyc_taxi_schema
    AUTHORIZATION nycrideshare;

CREATE SCHEMA public
    AUTHORIZATION nycrideshare;
```

4. Install PostGIS. After installation add the extension using the query below. Check if the tables and functions are created under the `public` schema before and after running the below query.

```SQL
CREATE EXTENSION postgis
    SCHEMA public
    VERSION "3.1.1";
```
5. Run the `final_project.ipynb` to create the tables needed for the project and populate them.

## Geopandas installation instructions for Windows
1. These steps assume that you have installed wheel (pip install *.whl on cmd).

2. Go to Unofficial Windows Binaries for Python Extension Packages.

3. Download on a specific folder the following binaries: GDAL, Pyproj, Fiona, Shapely and Geopandas matching the version of Python, and whether the 32-bit or 64-bit OS is installed on your laptop. (E.g. for Python v3.7x (64-bit), GDAL package should be GDAL‑3.1.2‑cp37‑cp37m‑win_amd64.whl.)

4. Use Command Prompt and go to the folder where you have downloaded the binaries

5. Important: The following order of installation using pip install is necessary. Be careful with the filename. It should work if the filename is correct: (Tip: Type “pip install” followed by a space and type the first two letters of the binary and press Tab. (e.g. pip install gd(press Tab))
  * `pip install .\GDAL-3.1.1-cp37-cp37m-win_amd64.whl`
  * `pip install .\pyproj-2.6.1.post1-cp37-cp37m-win_amd64.whl`
  * `pip install .\Fiona-1.8.13-cp37-cp37m-win_amd64.whl`
  * `pip install .\Shapely-1.7.0-cp37-cp37m-win_amd64.whl`
  * `pip install .\geopandas-0.8.0-py3-none-any`
