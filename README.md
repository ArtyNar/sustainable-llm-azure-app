# sustainable-llm-azure-app

See `api/function_app.py` for backend code that:

- Interacts with Azure OpenAI LLM modesl
- Stores and gathers prompt data in Azure Tables
- Interacts with Electricity Maps API to gather Carbon Intensity data

All API keys are accessed as environment variables. 

![alt text](Diagram.png)