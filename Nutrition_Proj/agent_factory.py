from agents import Agent
from db import calorie_lookup_tool, safe_exa_search
from mcp_config import get_exa_search_mcp
from guardrails import food_topic_guardrail
from config import get_github_model
from pydantic import BaseModel, Field
from typing import List

class CalorieData(BaseModel):
    food_item: str = Field(description="The name of the breakfast option (e.g., 'Greek Yogurt Parfait')")
    calories: int = Field(description="The total calculated calorie content as an integer (e.g., 340)")

class AdvisorResponse(BaseModel):
    text_response: str = Field(description="Your detailed breakfast plan and explanation in markdown format.")
    chart_data: List[CalorieData] = Field(description="A list of each food item and its corresponding total calorie value.")

def build_agents():
    """Assembles and returns all configured agents as a dictionary."""
    
    exa_search_mcp = get_exa_search_mcp()

    llm_model = get_github_model()

    # 1. Healthy Breakfast Planner Agent (Base)
    healthy_breakfast_planner_agent = Agent(
        name="breakfast_planner_assistant",
        instructions="""
        * You are a helpful assistant that helps with healthy breakfast choices.
        * You give concise answers.
        Given the user's preferences prompt, come up with different breakfast meals that are healthy and fit for a busy person.
        * Explicitly mention the meal's names in your response along with a sentence of why this is a healthy choice.
        """,
        model=llm_model,
   )

    # 2. Nutrition Assistant (Guarded)
    calorie_agent_with_search_guarded = Agent(
        name="nutrition_assistant",
        instructions="""
        * You are a helpful nutrition assistant giving out calorie information.
        * You give concise answers.
        * You follow this workflow:
            0) First, use the calorie_lookup_tool... [Truncated for brevity, keep your original text here]
        * Don't use the calorie_lookup_tool more than 10 times.
        * You only answer questions about food.
        * You give concise answers.
        3. Limit your search to a maximum of 1 or 2 results.
        * Don't use the calorie_lookup_tool more than 10 times.
        * CRITICAL: When using Exa Search, ALWAYS limit your search to a maximum of 2 results and request short summaries to save tokens. Do not fetch full web pages.
        * IMPORTANT: The search tool ONLY accepts a single search string. Do not pass any extra parameters.
        """,
        tools=[calorie_lookup_tool], 
        # mcp_servers=[exa_search_mcp],
        input_guardrails=[food_topic_guardrail],
        model=llm_model,
    )

    # Convert agents to tools
    calorie_calculator_tool = calorie_agent_with_search_guarded.as_tool(
        tool_name="calorie_calculator",
        tool_description="Use this tool to calculate the calories of a meal and it's ingredients"
    )
    
    breakfast_planner_tool = healthy_breakfast_planner_agent.as_tool(
        tool_name="breakfast_planner",
        tool_description="Use this tool to plan a a number of healthy breakfast options"
    )

    # 3. Breakfast Price Checker
    breakfast_price_checker_agent = Agent(
        name="breakfast_price_checker_agent",
        instructions="""
        * You check prices for breakfast ingredients using the safe_exa_search tool.
        * IMPORTANT: The search tool ONLY accepts a single search string (the 'query'). Do not pass any other parameters.
        * Pass a simple, direct query like: "average price of a dozen eggs 2024"
        * Output the final meal name, ingredients, calories, and price in Markdown.
        """,
        # mcp_servers=[exa_search_mcp],
        tools=[safe_exa_search],
        model=llm_model,
    )

    price_checker_tool = breakfast_price_checker_agent.as_tool(
        tool_name="price_checker",
        tool_description="Use this tool to find the real-world prices of the ingredients."
    )

    # 4. Main Breakfast Advisor (The Orchestrator)
    breakfast_advisor_guarded = Agent(
        name="breakfast_advisor_guarded_agent",
        instructions="""
        * You are a breakfast advisor. Come up with meal plans based on user preferences.
        * WORKFLOW:
          1. Call the 'breakfast_planner' tool to generate options.
          2. Call the 'calorie_calculator' tool to compute calories for the ingredients.
          3. CRITICAL: Once you have options and calories, immediately execute the 'transfer_to_breakfast_price_checker_agent' tool.
        * Do not try to generate final pricing yourself; you MUST use the transfer tool.
        * CRITICAL TOOL LIMITATION: You must BATCH your requests. Do NOT call the calorie or price tools multiple times. Pass ALL the meals and ingredients into the tools in a SINGLE combined text string.
        """,
        tools=[breakfast_planner_tool, calorie_calculator_tool, price_checker_tool],
        # handoff_description="Create a concise breakfast recommendation based on the user's preferences. Use Markdown format.",
        # handoffs=[breakfast_price_checker_agent],
        input_guardrails=[food_topic_guardrail],
        model=llm_model,
        output_type=AdvisorResponse
    )

    return {
        "nutrition_agent": calorie_agent_with_search_guarded,
        "breakfast_advisor": breakfast_advisor_guarded,
        # "mcp_server": exa_search_mcp
    }