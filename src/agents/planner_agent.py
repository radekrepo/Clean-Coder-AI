from langchain.output_parsers import XMLOutputParser
from typing import TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph
from dotenv import load_dotenv, find_dotenv
from src.utilities.print_formatters import print_formatted, print_formatted_content_planner
from src.utilities.util_functions import check_file_contents, convert_images, get_joke, read_coderrules, list_directory_tree
from src.utilities.langgraph_common_functions import after_ask_human_condition
from src.utilities.user_input import user_input
from src.utilities.graphics import LoadingAnimation
from src.utilities.llms import init_llms_planer
import os
from typing import Optional
from pydantic import BaseModel, Field


load_dotenv(find_dotenv())

llms_planners = init_llms_planer(run_name="Planner")
llm_planner = llms_planners[0].with_fallbacks(llms_planners[1:])
# copy planers, but exchange config name
llm_voter = llm_planner.with_config({"run_name": "Voter"})


class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    voter_messages: Sequence[BaseMessage]


parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

with open(f"{parent_dir}/prompts/planer_system.prompt", "r") as f:
    planer_system_prompt_template = f.read()
with open(f"{parent_dir}/prompts/voter_system.prompt", "r") as f:
    voter_system_prompt_template = f.read()

voter_system_message = SystemMessage(content=voter_system_prompt_template)

animation = LoadingAnimation()
# node functions
def call_planers(state):
    messages = state["messages"]
    nr_plans = 3
    print_formatted(get_joke(), color="green")
    plan_propositions_messages = llm_planner.batch([messages for _ in range(nr_plans)])
    for i, proposition in enumerate(plan_propositions_messages):
        state["voter_messages"].append(AIMessage(content="_"))
        state["voter_messages"].append(HumanMessage(content=f"Proposition nr {i+1}:\n\n" + proposition.content))

    print("Choosing the best plan...")
    chain = llm_voter | XMLOutputParser()
    response = chain.invoke(state["voter_messages"])

    choice = int(response["response"][2]["choice"])
    plan = plan_propositions_messages[choice - 1]

    state["messages"].append(plan)

    # Process and print the content
    print_formatted(f"Chosen plan:", color="light_blue")
    print_formatted_content_planner(plan.content)
    print_formatted(f"\nPlease read the plan carefully. Never accept plan you don't understand.", color="light_blue")

    return state


def call_planer(state):
    messages = state["messages"]
    print_formatted(get_joke(), color="green")
    animation.start()
    response = llm_planner.invoke(messages)
    animation.stop()
    print_formatted_content_planner(response.content)
    if response.ask_researcher:
        print_formatted(f"I have a question to Researcher!: {response.ask_researcher}", color="light_red")
    state["messages"].append(response.content)

    return state


def ask_human_planner(state):
    human_message = user_input("Type (o)k if you accept or provide commentary. ")
    if human_message in ['o', 'ok']:
        state["messages"].append(HumanMessage(content="Approved by human"))
    else:
        state["messages"].append(HumanMessage(
            content=f"Plan been rejected by human. Improve it following his commentary: {human_message}"
        ))
    return state


def call_model_corrector(state):
    messages = state["messages"]
    animation.start()
    response = llm_planner.invoke(messages)
    animation.stop()
    print_formatted_content_planner(response.content)
    if response.ask_researcher:
        print_formatted(f"I have a question to Researcher!: {response.ask_researcher}", color="light_red")
    state["messages"].append(response.content)

    return state


multiple_planers = False
# workflow definition
researcher_workflow = StateGraph(AgentState)

if multiple_planers:
    researcher_workflow.add_node("planers", call_planers)
else:
    researcher_workflow.add_node("planers", call_planer)
researcher_workflow.add_node("agent", call_model_corrector)
researcher_workflow.add_node("human", ask_human_planner)
researcher_workflow.set_entry_point("planers")

researcher_workflow.add_edge("planers", "human")
researcher_workflow.add_edge("agent", "human")
researcher_workflow.add_conditional_edges("human", after_ask_human_condition)

researcher = researcher_workflow.compile()


def planning(task, text_files, image_paths, work_dir, dir_tree=None, coderrules=None):
    if not dir_tree:
        dir_tree = list_directory_tree(work_dir)
    if not coderrules:
        coderrules = read_coderrules()
    file_contents = check_file_contents(text_files, work_dir, line_numbers=False)
    planer_system_message = SystemMessage(content=planer_system_prompt_template.format(project_rules=coderrules, file_contents=file_contents, dir_tree=dir_tree))
    print_formatted("📈 Planner here! Create plan of changes with me!", color="light_blue")
    images = convert_images(image_paths)
    message_content_without_imgs = f"Task:\n'''{task}'''"
    message_without_imgs = HumanMessage(content=message_content_without_imgs)
    message_images = HumanMessage(content=images)

    inputs = {
        "messages": [planer_system_message, message_without_imgs, message_images],
        "voter_messages": [voter_system_message, message_without_imgs],
    }
    planner_response = researcher.invoke(inputs, {"recursion_limit": 50})["messages"][-2]

    return planner_response


if __name__ == "__main__":
    task = "Test task"
    work_dir = os.getenv("WORK_DIR")
    planning(task, work_dir=work_dir)
