from langchain.tools import tool
from todoist_api_python.api import TodoistAPI
import os
from src.utilities.print_formatters import print_formatted
from src.utilities.manager_utils import actualize_progress_description_file, move_task
from src.utilities.user_input import user_input
from src.utilities.graphics import task_completed_animation
from src.utilities.util_functions import join_paths
from dotenv import load_dotenv, find_dotenv
from single_task_coder import run_clean_coder_pipeline
import uuid
import requests
from requests.exceptions import HTTPError
import json


load_dotenv(find_dotenv())
load_dotenv()

work_dir = os.getenv('WORK_DIR')
load_dotenv(join_paths(work_dir, ".clean_coder/.env"))
todoist_api_key = os.getenv('TODOIST_API_KEY')
todoist_api = TodoistAPI(todoist_api_key)
TOOL_NOT_EXECUTED_WORD = "Tool not been executed. "


@tool
def add_task(task_name, task_description, order):
    """Add new task to Todoist.
Think very carefully before adding a new task to know what do you want exactly. Explain in detail what needs to be
done in order to execute task.
Avoid creating new tasks that have overlapping scope with old ones - modify or delete old tasks first.
tool_input:
:param task_name: name of the task. Good name is descriptive, starts with a verb and usually could be fitted in formula
'To complete this task, I need to $TASK_NAME'.
:param task_description: detailed description of what needs to be done in order to implement task.
Good description includes:
- Definition of done (required) - section, describing what need to be done with acceptance criteria.
- Resources (optional) - Include here all information that will be helpful for developer to complete task. Example code
you found in internet, files dev need to use, technical details related to existing code programmer need to pay
attention on.
:param order: order of the task in project.
"""
    human_message = user_input("Type (o)k to agree or provide commentary.")
    if human_message not in ['o', 'ok']:
        return TOOL_NOT_EXECUTED_WORD + f"Action wasn't executed because of human interruption. He said: {human_message}"

    try:
        todoist_api.add_task(
            project_id=os.getenv('TODOIST_PROJECT_ID'),
            content=task_name,
            description=task_description,
            order=order,
        )
    except HTTPError:
        raise Exception(f"Are you sure Todoist project (ID: {os.getenv('TODOIST_PROJECT_ID')}) exists?")
    return "Task added successfully"


@tool
def modify_task(task_id, new_task_name=None, new_task_description=None, delete=False):
    """Modify task in project management platform (Todoist).
tool_input:
:param task_id: id of the task.
:param new_task_name: new name of the task (optional).
:param new_task_description: new detailed description of what needs to be done in order to implement task (optional).
:param delete: if True, task will be deleted.
"""
    try:
        task_name = todoist_api.get_task(task_id).content
    except HTTPError:
        raise Exception(f"Are you sure Todoist project (ID: {os.getenv('TODOIST_PROJECT_ID')}) exists?")
    human_message = user_input(f"I want to {'delete' if delete else 'modify'} task '{task_name}'. Type (o)k or provide commentary. ")
    if human_message not in ['o', 'ok']:
        return TOOL_NOT_EXECUTED_WORD + f"Action wasn't executed because of human interruption. He said: {human_message}"

    update_data = {}
    if new_task_name:
        update_data['content'] = new_task_name
    if new_task_description:
        update_data['description'] = new_task_description
    if update_data:
        todoist_api.update_task(task_id=task_id, **update_data)

    if delete:
        todoist_api.delete_task(task_id=task_id)
        return "Task deleted successfully"

    return "Task modified successfully"


@tool
def reorder_tasks(task_items):
    """Reorder tasks in project management platform (Todoist).
    tool_input:
    :param task_items: list of dictionaries with 'id' (str) and 'child_order' (int) keys.
    Example:
    {
    "tool": "reorder_tasks",
    "tool_input": {
        task_items: [
        {"id": "123", "child_order": 0},
        {"id": "456", "child_order": 1},
    ]

}
    """
    command = {
        "type": "item_reorder",
        "uuid": str(uuid.uuid4()),
        "args": {
            "items": task_items
        }
    }
    commands_json = json.dumps([command])
    response = requests.post(
        "https://api.todoist.com/sync/v9/sync",
        headers={"Authorization": f"Bearer {todoist_api_key}"},
        data={"commands": commands_json}
    )
    return "Tasks reordered successfully"


@tool
def create_epic(name):
    """
Create an epic to group tasks with similar scope.
tool_input:
:param name: short description of functionality epic is about.
"""
    print(f"project id: {os.getenv('TODOIST_PROJECT_ID')}")
    section = todoist_api.add_section(name=name, project_id=os.getenv('TODOIST_PROJECT_ID'))
    return f"Epic {section} created successfully"


@tool
def modify_epic(epic_id, new_epic_name=None, delete=False):
    """Modify an epic in project management platform (Todoist).
tool_input:
:param epic_id: id of the epic.
:param new_epic_name: new name of the epic (optional).
:param delete: if True, epic will be deleted with all tasks inside.
"""
    if delete:
        todoist_api.delete_section(section_id=epic_id)
        return "Epic deleted successfully"

    todoist_api.update_section(section_id=epic_id, name=new_epic_name)
    return "Epic modified successfully"


@tool
def finish_project_planning(dummy):
    """Call that tool to fire execution of top task from list. Use tool when all task in Todoist correctly reflect work. No extra tasks or tasks with
overlapping scope allowed.
tool_input:
dummy: just write "ok"
"""
    human_message = user_input(
        "Project planning finished. Provide your proposition of changes in task list or type (o)k to continue...\n"
    )
    if human_message not in ['o', 'ok']:
        return TOOL_NOT_EXECUTED_WORD + human_message

    # first_epic_id = todoist_api.get_sections(project_id=os.getenv('TODOIST_PROJECT_ID'))[0].id
    # tasks_first_epic = todoist_api.get_tasks(project_id=os.getenv('TODOIST_PROJECT_ID'), section_id=first_epic_id)
    # if not tasks_first_epic:
    #     return TOOL_NOT_EXECUTED_WORD + "Closest epic is empty. Close it if its scope been completely executed or add tasks into it if not."
    # # Get first task and it's name and description
    task = todoist_api.get_tasks(project_id=os.getenv('TODOIST_PROJECT_ID'))[0]
    task_name_description = f"{task.content}\n{task.description}"

    # Execute the main pipeline to implement the task
    print_formatted(f"\nAsked programmer to execute task: {task_name_description}\n", color="light_blue")
    run_clean_coder_pipeline(task_name_description, work_dir)

    # ToDo: git upload

    # Ask tester to check if changes have been implemented correctly
    tester_query = f"""Please check if the task has been implemented correctly.

    Task: {task.content}
    """
    tester_response = user_input(tester_query)

    actualize_progress_description_file(task_name_description, tester_response)

    # Mark task as done
    todoist_api.close_task(task_id=task.id)

    task_completed_animation()



if __name__ == "__main__":
    add_task.invoke({"task_name":"Dziki pies", "task_description": "Jakis tam opis", "order": 0, "epic_id": None})
