from langchain_openai.chat_models import ChatOpenAI
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
import operator
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.graph import StateGraph
from dotenv import load_dotenv, find_dotenv
from langchain.tools.render import render_text_description
from langchain.tools import tool
from langchain_community.chat_models import ChatOllama
from tools.tools import list_dir, see_file, see_image
from utilities.util_functions import check_file_contents, find_tool_json, print_wrapped
from utilities.langgraph_common_functions import call_model, call_tool, ask_human, after_ask_human_condition


load_dotenv(find_dotenv())


@tool
def final_response(reasoning, files_for_executor):
    """That tool outputs list of files executor will need to change and paths to graphical patterns if some.
    Use that tool only when you 100% sure you found all the files Executor will need to modify.
    If not, do additional research.
    'tool_input': {
        "reasoning": "Reasoning what files will be needed.",
        "files_to_work_on": ["List", "of", "files."],
        "template_images": ["List of image paths", "that be used as graphical patterns."]
    }
    """
    pass


tools = [list_dir, see_file, final_response]
rendered_tools = render_text_description(tools)

llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.2)
#llm = ChatOllama(model="openchat") #, temperature=0)


class AgentState(TypedDict):
    messages: Sequence[BaseMessage]

project_knowledge = "Common styles for memorial profile pages are placed in assets/scss/MemorialProfile.scss"

tool_executor = ToolExecutor(tools)
system_message = SystemMessage(
        content="You are expert in filesystem research and choosing right files."
                "Your research is very careful - rather check more files then less. If you not if you need to check some file or not - you check it. "
                "Good practice you follow is when found important dependencies that point from file you checking to "
                "other file, you check other file also. "
                "At your final response, you choosing only needed files, while leaving that not needed. "
                "some files do not require modification, but can be used as a template - also include them."
                "Do filesystem research and provide existing files that executor will need to change or take a look at "
                "in order to do his task. NEVER recommend file you haven't seen yet. "
                "Never recommend files that not exist but need to be created."
                "Start your research from '/' dir."
                "Knowledge about project:\n"
                f"{project_knowledge}\n\n"
                "\n\n"
                "You have access to following tools:\n"
                f"{rendered_tools}"
                "\n\n"
                "Generate response using next json blob (strictly follow it!). That json need to be part of your response:"
                "```json"
                "{"
                " 'tool': '$TOOL_NAME',"
                " 'tool_input': '$TOOL_PARAMS',"
                "}"
                "```"
    )


# node functions
def call_model_researcher(state):
    return call_model(state, llm)


def call_tool_researcher(state):
    return call_tool(state, tool_executor)


# Logic for conditional edges
def after_agent_condition(state):
    last_message = state["messages"][-1]

    if last_message.tool_call["tool"] == "final_response":
        return "human"
    else:
        return "tool"


# workflow definition
researcher_workflow = StateGraph(AgentState)

researcher_workflow.add_node("agent", call_model_researcher)
researcher_workflow.add_node("tool", call_tool_researcher)
researcher_workflow.add_node("human", ask_human)

researcher_workflow.set_entry_point("agent")

researcher_workflow.add_conditional_edges(
    "agent",
    after_agent_condition,
)
researcher_workflow.add_conditional_edges(
    "human",
    after_ask_human_condition,
)
researcher_workflow.add_edge("tool", "agent")

researcher = researcher_workflow.compile()


def research_task(task):
    print("Researcher starting its work")
    inputs = {"messages": [system_message, HumanMessage(content=f"task: {task}")]}
    researcher_response = researcher.invoke(inputs, {"recursion_limit": 100})["messages"][-2]

    tool_json = find_tool_json(researcher_response.content)
    text_files = tool_json["tool_input"]["files_to_work_on"]
    file_contents = check_file_contents(text_files)

    image_paths = tool_json["tool_input"]["template_images"]
    images = []
    for image_path in image_paths:
        images.append(
            {
                "type": "text",
                "text": image_path,
            }
        )
        images.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{see_image(image_path)}",
                },
            }
        )
        '''
        images.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": see_image(image_path),
                },
            }
        )
        '''

    message_content = [f"task: {task},\n\n files: {file_contents}"] + images
    message_for_planner = HumanMessage(content=message_content)

    return message_for_planner, text_files, file_contents