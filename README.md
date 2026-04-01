
# Welcome
Hello I'm YuChen. This project aims to solve the Text-to-SQL issue by Langgraph new agent framework **Deep Agent**.

## Expected Abilities
1. Flexible Utilization: User only need to ask in natural language and attatch the datasets as input.
2. Automatically Data Schema Analyze: System will read and understand the user query and data schema.
3. Text-to-SQL: Transfer user's query to SQL language.
4. Visualization Present: Present the analysis to answer user's query.

## Present
### Example 1: Dataset Analysis
- Task: `Analyze the count of surviving males over age 20 in the Titanic dataset.`
- Input: `titanic_dataset.csv`
- Response: `在這次的數據分析任務中，您要求分析泰坦尼克號數據集中20歲以上存活男性的數量。根據分析結果，泰坦尼克號數據集中20歲以上的存活男性數量為64人。`

## Architecture
``` plaintext
User Question
     ↓
Intent Agent 
     └─ Check if user's question aligns with the system's capabilities.
     ↓
Planning Agent 
     └─ Orchestrate specialized sub-agents and manage complex, multi-step procedure.
     ↓
Specialized Sub-agents
     ├─  Dataframe Agent
     │    ├─ Helper Tools
     │    │    ├─ execute_python()
     │    ├─ Filesystem Tools (optional)
     │    │    ├─
     │    │    ├─ ls
     │    │    ├─ grep
     │    │    ├─ read_file
     │    │    ├─ write_file
     │    │    └─ edit_file
     └─ Other Specialized Sub-agents ... (waiting)
     ↓
Summary Agent
     ↓
Formatted Answer
```


## Reference
### Reading Reference
- [LangChain - DeepAgents Core Components](https://docs.langchain.com/oss/python/deepagents/harness)
    - Backend Component Settings 
### Datasets Reference
- [Titanic - Machine Learning from Disaster](https://www.kaggle.com/competitions/titanic/data)