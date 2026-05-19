import os
from openai import AsyncOpenAI
from agents import set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

# 1. Turn off OpenAI telemetry globally
set_tracing_disabled(True)

def get_github_model():
    """Builds and returns the configured GitHub/Azure model object."""
    
    # 2. Build the explicit client
    custom_client = AsyncOpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ.get("OPENAI_API_KEY") 
    )
    
    # 3. Wrap it in the framework's model class
    github_model = OpenAIChatCompletionsModel(
        openai_client=custom_client,
        model="gpt-4o-mini" # Or "Meta-Llama-3.3-70B-Instruct" 
    )
    
    return github_model