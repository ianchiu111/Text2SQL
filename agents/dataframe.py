import json, re
from typing import Dict, Any

import pandas as pd
from pathlib import Path
from utils.AI_utils.openai_api_helper import LLMClient

from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend 

from agents.prompts import get_dataframe_agent_prompt
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from agents.base import BaseAgent


class DataframeAgent(BaseAgent):
    def __init__(self, AgentState, llm_client=None):
        self.AgentState = AgentState
        self.llm = llm_client.llm

        BASE_DIR = Path(__file__).parent
        self.DATA_DIR = BASE_DIR / "data"

        # DeepAgents core component: Grants agents direct filesystem read/write access. warning "Security Warning"
        self.dataframeAgent_backend_config = FilesystemBackend(
            root_dir=self.DATA_DIR,
            virtual_mode=False
        )

    def _safe_parse_json(self, text: str) -> dict:
        if isinstance(text, dict):
            return text
        if not text or not isinstance(text, str):
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            cleaned = re.sub(r"```json|```", "", text).strip()
            m = re.search(r"\{[\s\S]*\}", cleaned)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError as e:
                    print(f"fallback decode error: {e}\nOrigin Content: {text}")
                    return {}
            else:
                print(f"無法找到 json object, Origin Content: {text}")
                return {}

    # Define a free, local Python execution tool
    @tool
    def execute_python(code: str):
        """
        Execute python code locally. 
        IMPORTANT: MUST use print() to output the final result or any values to see the results.
        """
        repl = PythonREPL() 
        try:
            result = repl.run(code)
            print(f"Execution Codes:\n{code}\n, Execution Result:\n{result}")
            return f"Execution Codes:\n{code}\n, Execution Result:\n{result}"
        
        except Exception as e:
            return f"Error during execution:\n{e}"

    def run(self, state: Dict[str, Any]) -> Command:

        print(">>>>Dataframe Working<<<<")

        planning = state.get("planning")

        for plan in planning:
            
            if plan.get("finish"):
                continue
            else:
                
                question = plan.get("question")
                dataset_path = plan.get("dataset_path")

                prompt = get_dataframe_agent_prompt()

                dataframe_agent = create_deep_agent(
                    backend=self.dataframeAgent_backend_config,
                    model = self.llm,
                    tools=[self.execute_python],
                    context_schema=self.AgentState,
                    system_prompt=prompt,
                )

                response = dataframe_agent.invoke(
                    {"messages": f"User Question: {question}, Dataset Path: {dataset_path}"}
                )
                content = response["messages"][-1].content

                # set finish to True and update answer in plan
                plan["finish"] = True
                plan["answer"] = content

                break

        # update the state in agent
        update = {
            "planning": planning,
        }
        return Command(update=update)
