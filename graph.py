import os, json
import time
from typing import List, Dict, Any, TypedDict

from langgraph.graph import StateGraph, END, START

from agents.base import BaseAgent
from agents.intent import IntentAgent
from agents.planning import PlanningAgent
from agents.dataframe import DataframeAgent
from agents.summary import SummaryAgent


from utils.AI_utils.openai_api_helper import LLMClient

from dotenv import load_dotenv
load_dotenv(".env")


class AgentState(TypedDict, total=False):
    origin_query: str
    next_action: str
    response: str

    original_planning: List[Dict[str, Any]]     # for checking agent's planning todo list, not for routing.
    planning: List[Dict[str, Any]]    # for agent routing
    # [
    #     {
    #         "task_index": int,   
    #         "planning_type": str,
    #         "question": str,
    #         "answer": str,
    #         "dataset_path": str,
    #         "finish": bool,
    #     },
    #     {...}
    # ]

def _stringify(self, obj: Any) -> str:
    """Pretty-print dict / list, otherwise str()."""
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, ensure_ascii=False, indent=2)
    return str(obj)

def run_agent(query: str) -> None:
    llm = LLMClient()

    intent_agent = IntentAgent(llm_client=llm)
    planning_agent = PlanningAgent(llm_client=llm)
    dataframe_agent = DataframeAgent(AgentState=AgentState, llm_client=llm)
    summary_agent = SummaryAgent(llm_client=llm)

    def _intent_router(state: AgentState) -> str:
        print(state.get("next_action"))
        if state.get("next_action") == "next_agent":
            return "planning" 
        else:
            return "summary" 

    def _planning_router(state: AgentState):
        planning = state.get("planning")
        print(f"Planning Agent's Planning: {json.dumps(planning, ensure_ascii=False, indent=2)}")

        for plan in planning:

            if plan.get("finish"):
                continue
            else:
                type = plan.get("planning_type")
                if  type == "data_analysis":
                    print(f"Routing based on: {type}")
                    return "dataframe"
                else:
                    print("return to summary")
                    return "summary"   
                
        print("All tasks are finished, return to summary")
        return "summary"      

    graph = StateGraph(state_schema=AgentState)
    graph.add_node("intent", intent_agent)
    graph.add_node("planning", planning_agent)
    graph.add_node("dataframe", dataframe_agent)
    graph.add_node("summary", summary_agent)

    graph.add_edge(START, "intent")
    graph.add_conditional_edges("intent", _intent_router, ["planning", "summary"])  
    graph.add_conditional_edges("planning", _planning_router, ["dataframe", "summary"]) 
    graph.add_conditional_edges("dataframe", _planning_router, ["dataframe", "summary"]) 
    graph.add_edge("summary", END)

    agent_graph = graph.compile()

    init_state: AgentState = {
        "origin_query": query,
        "next_action": "",
        "response": "",

        "original_planning": [],
        "planning": [],
    }

    result = agent_graph.invoke(init_state)

    print("\n=== Completed Agent State: ===\n", result)

    return result


if __name__ == "__main__":
    start_time = time.time()
    # result = run_agent("Use python to analyze how many alive males whose age is more than 20 in the titanic dataset.(/Users/yuchen/Visual_Studio_Code/DeepAgent_text2sql/data/titanic_dataset.csv)") 
    # result = run_agent("Analyze the count of surviving males over age 20 in the Titanic dataset.(/Users/yuchen/Visual_Studio_Code/DeepAgent_text2sql/data/titanic_dataset.csv)") 
    # result = run_agent("Clean the Titanic dataset to make sure there are no missing values and save it for me.(/Users/yuchen/Visual_Studio_Code/DeepAgent_text2sql/data/titanic_dataset.csv)") 
    result = run_agent("Clean the Titanic dataset to make sure there are no missing values and visualize the age and distribution with picture results.(/Users/yuchen/Visual_Studio_Code/DeepAgent_text2sql/data/titanic_dataset.csv)") 

    response = result.get("response", "")
    
    print("\n=== Final Response ===\n")
    print(response)
    print(f"⏰ Total process time: {time.time()-start_time}")
