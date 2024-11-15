import uuid
import aiohttp
import asyncio
from fastapi import BackgroundTasks
from datetime import datetime

class DataModel:
    def __init__(self, uid, file_id, status):
        self.uid     = uid
        self.file_id = file_id  # Store the file ID
        self.status  = status
        self.result  = None
        self.message = None
        self.execution_time = None

model = []
curr_index = 0
ML_MODEL_URL = "http://localhost:8071/test"
prediction_lock = asyncio.Lock()

async def process_prediction(file_id: str):
    global curr_index
    async with prediction_lock:
        try:
            model[curr_index].status = 'processing'
            start = datetime.now()

            async with aiohttp.ClientSession() as session:
                async with session.post(ML_MODEL_URL, json={'file_id': file_id}) as response:
                    model[curr_index].status = response.status
                    if response.status == 200:
                        result = await response.json()
                        model[curr_index].result  = result
                        model[curr_index].massage = ''
                    else:
                        model[curr_index].result  = ''
                        model[curr_index].massage = await response.text()
        except Exception as e:
            model[curr_index].result  = ''
            model[curr_index].status  = 500
            model[curr_index].massage = str(e)
        finally:
            execution_time = (datetime.now() - start).total_seconds()
            model[curr_index].execution_time = execution_time
            curr_index += 1

        # Process the next item in the model list, if available
        if curr_index < len(model):
            next_model = model[curr_index]
            if next_model and next_model.status == 'waiting':
                asyncio.create_task(process_prediction(next_model.file_id))


async def upload_file(file_id: str):
    generated_id = str(uuid.uuid4())

    new_model = DataModel(generated_id, file_id, 'waiting')
    model.append(new_model)

    # Start processing if no tasks are running
    processing_tasks = [i for i in model if i.status == 'processing']
    if not processing_tasks:
        asyncio.create_task(process_prediction(file_id))

    return {"id": generated_id}


def get_result_by_id(id: str):
    result = [i for i in model if i.uid == id]    
    if result:
        if result[0].status == 'waiting':
            return {
                'id': id,
                'status': 'waiting'
            }
        
        if result[0].status == 'processing':
            return {
                'id': id,
                'status': 'processing'
            }
        
        return {
            'id': id,
            'http_code': result[0].status,
            'status': 'completed',
            'massage': result[0].massage,
            'execution_time': result[0].execution_time if hasattr(result[0], 'execution_time') else None,
            'result': result[0].result if result[0].result is not None else "Result not available yet",
        }
    return {"error": "ID not found"}
