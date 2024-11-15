import fastapi
import time
from fastapi import Form, Body

from app_logic import *

app = fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"message": "IBrain2U API System"}


@app.post("/predict")
async def predict(file_id: str):
    return await upload_file(file_id)


@app.get('/result/{id}')
def get_result(id: str):
    return get_result_by_id(id)


## Testing thingy
@app.post('/test')
def testing(file_id: str = Body(..., embed= True)):
    time.sleep(20)
    return {
        "1": 0.75,
        "2": 0.15,
        "3": 0.05,
        "4": 0.05
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8071)