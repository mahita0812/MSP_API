from fastapi import Request
from src.utils.constants import *
from src.services.regenerate_service import regenerate_mail_template
from src.controllers.database_controllers.tasks_db.update_task_feedback import update_task_feedback
from fastapi.responses import JSONResponse
from src.controllers.database_controllers.tasks_db.update_response import update_task_response
from src.controllers.database_controllers.tasks_db.update_task_feedback import update_task_feedback
from src.controllers.database_controllers.tasks_db.tasks import add_task
from src.services.fetch_previous_mails import fetch_prev_mails
from src.controllers.database_controllers.tasks_db.update_status import update_task_status
from src.controllers.database_controllers.tasks_db.update_failed_reason import update_failed_reason
import uuid, json

async def regenerate_mail(request:Request,user_id, db, trace_id):
    if(not trace_id):
        trace_id = str(uuid.uuid4())
    try:
        request_data = await request.json()
        body = request_data.get('body',None)
        subject = request_data.get('subject',None)
        llm_id = request_data.get('llm_id',None)

        await update_task_feedback(llm_id, db, 'Negative', user_id, trace_id)
        task_id = add_task(llm_id,[], user_id, db, trace_id)

        
        if body and llm_id and subject:

            previous_mails = await fetch_prev_mails(llm_id, db, trace_id)
            regenerated_mail_body = regenerate_mail_template(previous_mails,llm_id)
            
            mail_json_text = json.dumps({'subject':subject, 'body' : regenerated_mail_body})
            mail_json_form = json.loads(mail_json_text)
            await update_task_response(task_id, mail_json_form,db,user_id,trace_id)
            update_task_status(task_id, db, 'Completed', user_id, trace_id)


            
            return JSONResponse(content={
                "subject":subject,
                "body": regenerated_mail_body,
                "llm_id": llm_id
            }, status_code = OK)
        else:
            error_msg = f"body or llm_id is missing in request body"
            return JSONResponse(content={"message":error_msg},status_code = UNPROCESSABLE_ENTITY)

    except Exception as e:
        error_msg = f"Error in regenerate_mail : {e}"
        update_failed_reason(task_id, db, error_msg, trace_id)
        return JSONResponse(content={"message":error_msg},status_code = INTERNAL_SERVER_ERROR)
    
    