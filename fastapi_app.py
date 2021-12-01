from connection import client

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class School(BaseModel):
    city: str
    control: str
    debt_mdn: str
    hcm2: str
    highdeg: str
    instnm: str
    insturl: str
    main: str
    city_state: str
    location: str
    tags: str
    st_fips: str
    
    
@app.get("/")
async def info():
    """Base Connection and Info. Great for testing your connecting Auth"""
    return {"message":"School Scoutr: for college searches over 9000"}
    

@app.get("/school/{id}")
async def get_school_info(school_name: str):
    """Returns a single """
    return client.get(index="schools", id=id)
    
@app.get("/schools")
async def get_school_by_query(query):
    
@app.get("/city")
async def get_schools_by_city(city)
    