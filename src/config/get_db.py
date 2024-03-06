from ..config.database import base,engine,session_local
from src.models.llm_model import LLM
from src.models.task_model import Task
from src.models.tickets import TicketBase
 
models = [LLM,Task,TicketBase]
 
base.metadata.create_all(bind=engine, tables=[model.__table__ for model in models])
 
def get_db():  
    db = session_local()
    try:
        yield db
    finally:
        db.close()