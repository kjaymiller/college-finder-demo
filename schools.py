import json
import pathlib

import eland
import pandas as pd

from connection import client


def gen_tags(row, fields):
    return [field for field in fields if row[field] == 1.0]


def _translate_code(json_file, df_column, if_None: str = "Unknown"):
    j_file = json.loads(pathlib.Path(json_file).read_text())
    return lambda x: j_file.get(str(x), if_None)


def parse_schools():
    converter_list = [
        (
            "RELAFFIL",
            _translate_code("translations/relaffil.json", "RELAFFIL", if_None="None"),
        ),
        ("CONTROL", _translate_code("translations/control.json", "CONTROL")),
        ("ST_FIPS", _translate_code("translations/st_fips.json", "ST_FIPS")),
        ("HIGHDEG", _translate_code("translations/high_deg.json", "HIGHDEG")),
    ]

    converters = {
        x: y for x, y in converter_list
    }  # To return "ST_FIPS": lambda x:st_fips_json.get(str(x), "Unknown"), etc

    column_values = {
        "INSTNM": str,
        "INSTURL": str,
        "CITY": str,
        "ST_FIPS": int,
        "PBI": float,
        "ANNHI": float,
        "TRIBAL": float,
        "AANAPII": float,
        "HSI": float,
        "NANTI": float,
        "HBCU": float,
        "CURROPER": float,
        "LATITUDE": float,
        "LONGITUDE": float,
        "MENONLY": float,
        "WOMENONLY": float,
        "CONTROL": int,
        "RELAFFIL": str,
        "HIGHDEG": str,
        "MAIN": float,
        "HCM2": float,
    }

    null_values = {
        "INSTURL": "",
        "CITY": "",
        "PBI": 0.0,
        "ANNHI": 0.0,
        "TRIBAL": 0.0,
        "AANAPII": 0.0,
        "HSI": 0.0,
        "NANTI": 0.0,
        "LATITUDE": 0.0,
        "LONGITUDE": 0.0,
        "HBCU": 0.0,
        "MENONLY": 0.0,
        "WOMENONLY": 0.0,
        "RELAFFIL": "None",
    }

    schools = pd.read_csv(
        "Most-Recent-Cohorts-All-Data-Elements.csv",
        usecols=list(column_values.keys()),
        converters=converters,
        dtype=column_values,
        low_memory=False,
    )

    schools.fillna(value=null_values, inplace=True)

    schools["location"] = schools.apply(
        lambda x: f"{x.LATITUDE}, {x.LONGITUDE}", axis=1
    )

    school_tags = [
        "PBI",
        "ANNHI",
        "TRIBAL",
        "AANAPII",
        "HBCU",
        "MENONLY",
        "WOMENONLY",
        ]

    schools["tags"] = schools.apply(lambda x: gen_tags(x, school_tags), axis=1)

    eland.pandas_to_eland(
        pd_df=schools,
        es_dest_index="schools",
        es_if_exists="replace",
        es_client=client,
        es_refresh=True,
        es_type_overrides={"location": "geo_point"},
    )


def parse_cities():
    # Use Alternames in the Future to Build Synonym Graph

    city_columns = [
        "geonameid",
        "city",
        "LATITUDE",
        "LONGITUDE",
        "state",
        "feature_class",
        "feature_code",
    ]

    base_cities = pd.read_csv(
        "US.txt",
        usecols=city_columns,
        sep="\t",
        low_memory=False,
        index_col="geonameid",
    )

    cities = base_cities[(base_cities["feature_class"] == "P") & (base_cities['feature_code']=='PPL')]
    cities.fillna(value="", inplace=True)

    cities["location"] = cities.apply(lambda x: f"{x.LATITUDE}, {x.LONGITUDE}", axis=1)
    return cities


def upload_cities(cities):
    return eland.pandas_to_eland(
        cities,
        es_dest_index="cities",
        es_if_exists="replace",
        es_client=client,
        es_refresh=True,
        es_type_overrides={
            "location": "geo_point",
            "city": "text",
        },
    )


if __name__ == "__main__":
    # parse_schools()
    cities = parse_cities()
    upload_cities(cities)