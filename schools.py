"""Uploads the US Dept of Education Data into an Elasticsearch instance"""

import json
import pathlib

import pandas as pd
from elasticsearch.helpers import bulk

from connection import local_client as client

unknown_or_empty_values = ["None", "Unknown"]


def _translate_code(
    json_file,
    if_none: str = "Unknown",
):
    """mapper to process values from json_files in translate directory"""
    j_file = json.loads(pathlib.Path(json_file).read_text(encoding="utf-8"))
    return lambda x: j_file.get(str(x), if_none)


def fix_links(url):
    """ensures INSTURL is the correct link format"""
    if not url.startswith("http"):
        return f"https://{url}"
    return url


def top_values(row, count=3) -> list:
    """sorter for percentage_mapper values.
    Designed to give a quick reference to most popular degree programs"""

    percentage_mapper_value_names = list(percentage_mapper.values())
    percentage_mapper_values = [row[pcip] for pcip in percentage_mapper_value_names]

    if sum(percentage_mapper_values) == 0.0:
        return []  # Filter Rankings when percentages are not provided

    sorted_pcip_rows = sorted(
        percentage_mapper_value_names, key=lambda x: row[x], reverse=True
    )
    return sorted_pcip_rows[:count]


percentage_mapper = json.loads(
    pathlib.Path("translations/degree_percentage.json").read_text(encoding="utf-8")
)


def gen_tags(row, fields):
    """Create Tags based on the fields in the tag_translation"""
    tag_translation = {
        "MENONLY": "Men Only",
        "WOMENONLY": "Women Only",
        "AANHI": "Alaska Native/Native Hawaiian",
        "TRIBAL": "Tribal",
        "AANAPII": "AAPI",
        "HSI": "Hispanic/Latinx",
        "PBI": "Black/BIPOC",
        "NANTI": "Native American (Non-Tribal)",
    }

    tags = []

    for field in fields:
        if row[field] and row[field] not in unknown_or_empty_values:

            if field in tag_translation:
                tags.append(tag_translation[field])

            elif row[field] == 1.0:
                tags.append(field)

            else:
                tags.append(row[field])
    return tags


def define_campus_type(row):
    """Translates Campus Type to Either Main or Branch/Satelite Campus"""
    if row["MAIN"] == "1":
        return "Main Campus"

    return "Branch/Satelite Campus"


def parse_schools():
    """Main Runner for script"""
    converter_list = [
        (
            "RELAFFIL",
            _translate_code("translations/relaffil.json", if_none="None"),
        ),
        ("CONTROL", _translate_code("translations/control.json")),
        ("ST_FIPS", _translate_code("translations/st_fips.json")),
        ("HIGHDEG", _translate_code("translations/high_deg.json")),
        ("INSTURL", fix_links),
    ]

    converters = dict(converter_list)

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
        "CONTROL": str,
        "RELAFFIL": str,
        "HIGHDEG": str,
        "MAIN": "str",
        "HCM2": float,
        "ADM_RATE": float,
        "ADM_RATE_ALL": float,
        "TUITIONFEE_IN": float,
        "TUITIONFEE_OUT": float,
        "DEBT_MDN": str,
        "PCTFLOAN": float,
        "PCIP01": float,
        "PCIP03": float,
        "PCIP04": float,
        "PCIP05": float,
        "PCIP09": float,
        "PCIP10": float,
        "PCIP11": float,
        "PCIP12": float,
        "PCIP13": float,
        "PCIP14": float,
        "PCIP15": float,
        "PCIP16": float,
        "PCIP19": float,
        "PCIP22": float,
        "PCIP23": float,
        "PCIP24": float,
        "PCIP25": float,
        "PCIP26": float,
        "PCIP27": float,
        "PCIP29": float,
        "PCIP30": float,
        "PCIP31": float,
        "PCIP38": float,
        "PCIP39": float,
        "PCIP40": float,
        "PCIP41": float,
        "PCIP42": float,
        "PCIP43": float,
        "PCIP44": float,
        "PCIP45": float,
        "PCIP46": float,
        "PCIP47": float,
        "PCIP48": float,
        "PCIP49": float,
        "PCIP50": float,
        "PCIP51": float,
        "PCIP52": float,
        "PCIP54": float,
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
        "ADM_RATE": 0.0,
        "ADM_RATE_ALL": 0.0,
        "TUITIONFEE_IN": 0,
        "TUITIONFEE_OUT": 0,
        "DEBT_MDN": 0.0,
        "PCTFLOAN": 0.0,
        "PCIP01": 0.0,
        "PCIP03": 0.0,
        "PCIP04": 0.0,
        "PCIP05": 0.0,
        "PCIP09": 0.0,
        "PCIP10": 0.0,
        "PCIP11": 0.0,
        "PCIP12": 0.0,
        "PCIP13": 0.0,
        "PCIP14": 0.0,
        "PCIP15": 0.0,
        "PCIP16": 0.0,
        "PCIP19": 0.0,
        "PCIP22": 0.0,
        "PCIP23": 0.0,
        "PCIP24": 0.0,
        "PCIP25": 0.0,
        "PCIP26": 0.0,
        "PCIP27": 0.0,
        "PCIP29": 0.0,
        "PCIP30": 0.0,
        "PCIP31": 0.0,
        "PCIP38": 0.0,
        "PCIP39": 0.0,
        "PCIP40": 0.0,
        "PCIP41": 0.0,
        "PCIP42": 0.0,
        "PCIP43": 0.0,
        "PCIP44": 0.0,
        "PCIP45": 0.0,
        "PCIP46": 0.0,
        "PCIP47": 0.0,
        "PCIP48": 0.0,
        "PCIP49": 0.0,
        "PCIP50": 0.0,
        "PCIP51": 0.0,
        "PCIP52": 0.0,
        "PCIP54": 0.0,
    }

    schools = pd.read_csv(
        "Most-Recent-Cohorts-All-Data-Elements.csv",
        usecols=list(column_values.keys()),
        converters=converters,
        dtype=column_values,
        low_memory=False,
    )

    schools.fillna(value=null_values, inplace=True)
    schools.rename(inplace=True, columns=percentage_mapper)

    schools["MAIN"] = schools.apply(lambda x: define_campus_type(x), axis=1)

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
        "HSI",
        "RELAFFIL",
    ]

    keep_tags = ["RELAFFIL"]

    schools["top_programs"] = schools.apply(lambda x: top_values(x), axis=1)

    schools["base_tags"] = schools.apply(lambda x: gen_tags(x, school_tags), axis=1)
    schools["tags"] = schools.apply(
        lambda x: [*x["top_programs"], *x["base_tags"]], axis=1
    )
    schools["city_state"] = schools.apply(
        lambda x: f"{x['CITY']}, {x['ST_FIPS']}", axis=1
    )

    drop_tags = [x for x in school_tags if x not in keep_tags]

    schools.drop(columns=drop_tags, inplace=True)

    synonym_mappings = {
        "properties": {
            "CITY": {
                "type": "keyword",
            },
            "CONTROL": {
                "type": "keyword",
            },
            "DEBT_MDN": {
                "type": "keyword",
            },
            "HCM2": {"type": "float"},
            "HIGHDEG": {
                "type": "keyword",
            },
            "INSTNM": {
                "type": "text",
            },
            "INSTURL": {
                "type": "keyword",
            },
            "MAIN": {
                "type": "keyword",
            },
            "city_state": {
                "type": "text",
            },
            "location": {"type": "geo_point"},
            "tags": {"type": "keyword"},
            "ST_FIPS": {"type": "keyword"},
        },
    }

    client.indices.create(
        index="schools",
        mappings=synonym_mappings,
    )
    bulk(
        client=client,
        index="schools",
        actions=schools.to_dict(orient="records"),
    )


if __name__ == "__main__":
    client.indices.delete(index="schools", ignore=[400, 404])
    parse_schools()
