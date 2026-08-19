from fastapi import FastAPI,  HTTPException
from pydantic import BaseModel
# pydantic used for parsing and validating the data coming from user end so that it doesnt occur an error if the data is in wrong form

# this creates the app (the waiter the one who sendes the message to the server by taking it from client with the help of API fastapi)
app = FastAPI() 

# this is a dict
todo_db = {
    1:{"title":"compelete todo list api","completed": False},
    2:{"title":"buy grocieries", "completed": False}
}

# this is basemodel of pydantic which is a bodyguard to protect and obey the enclosed format else will return in 422 error its a kind of a bouncer to send exactly this dictionary structure else return false
class todoitem(BaseModel):
    title:str
    completed: bool = False

# this is a decorator with get and then function defined to return todo_list means to help see whats the tasks in todo list like reading data
@app.get("/todos")
def get_all_todos():
    return{"tasks":todo_db}

# this is post which means it will help in creating data
@app.post("/todos")
def create_todo(item: todoitem):
    # this item.model_dump() turns the pydantic model into a normal python dict 
    new_id = max(todo_db.keys()) +1 if todo_db else 1
    todo_db[new_id] = item.model_dump()
    return {"message": "task added! ", "task":todo_db[new_id]}

# updating data (PUT)
@app.put("/todos/{todo_id}")
def update_todo(todo_id:int, item:todoitem):
    if todo_id not in todo_db:
        raise HTTPException(status_code=404, detail="task not found")

    todo_db[todo_id] = item.model_dump()
    return{"message":"task updated","task":todo_db[todo_id]}

# deleting data (DELETE)
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id:int):
    if todo_id not in todo_db:
        raise HTTPException(status_code = 404, detail="task not found")

    del todo_db[todo_id]
    return{"message":"task deleted sucessfully"}


