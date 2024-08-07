from fastapi import Body, FastAPI
from pydantic import BaseModel as BaseModel2
from typing import Optional
from SQL_generation import *
import logging

app = FastAPI()

#Define a model for incoming data
class Query(BaseModel2):
    user_query: str
    thread: str
    initial_state: bool
    verbose: Optional[bool] = False

# Define a route that accepts a POST request with data
@app.post("/get_results")
def get_results(query: Query=Body(...)):
    try:
        thread= get_thread(thread_id = query.thread)
        final_result= final_genai_function(user_query= query.user_query, thread= thread, is_initial_state = query.initial_state, verbose= query.verbose)
        return final_result
    except:
        logging.exception('Error')

# # Define a route with query parameters
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Optional[str] = None):
#     return {"item_id": item_id, "q": q}
        

