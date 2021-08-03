import pandas as pd
import json
import pathlib


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

def _translate_code(json_file, df_column, if_None: str="Unknown"):
    j_file = json.loads(pathlib.Path(json_file).read_text())
    return lambda x:j_file.get(str(x), if_None)

converter_list = [
         ("RELAFFIL", _translate_code("translations/relaffil.json", "RELAFFIL", if_None="None")),
         ("CONTROL", _translate_code("translations/control.json", "CONTROL")),
         ("ST_FIPS", _translate_code("translations/st_fips.json", "ST_FIPS")),
         ("HIGHDEG", _translate_code("translations/high_deg.json", "HIGHDEG")),
        ]

converters = {x:y for x,y in converter_list} # To return "ST_FIPS": lambda x:st_fips_json.get(str(x), "Unknown"), etc

schools = pd.read_csv(
    "Most-Recent-Cohorts-All-Data-Elements.csv",
    usecols=list(column_values.keys()),
    converters=converters,
    dtype=column_values,
    low_memory=False,
)


cities = pd.read_csv('US.txt', sep="\t", low_memory=False)
