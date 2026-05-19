from agents import Agent
from db import calorie_lookup_tool, safe_exa_search
from mcp_config import get_exa_search_mcp
from guardrails import food_topic_guardrail
from config import get_github_model

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
        """,
        tools=[calorie_lookup_tool], 
        mcp_servers=[exa_search_mcp],
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
        * You are a helpful assistant that takes multiple breakfast items (with ingredients and calories) and checks for the price of the ingredients.
        * Use the exa search to get an approximate price for the ingredients.
        * EXA SEARCH RULES (CRITICAL):
          1. Limit your search to 1 result per ingredient.
          2. NEVER fetch the full text or raw HTML of a webpage. 
          3. Extract ONLY the price and discard the rest of the text.
        * In your final output provide the meal name, ingredients with calories, and price for each meal.
        * Use markdown and be as concise as possible.
        """,
        # mcp_servers=[exa_search_mcp],
        tools=[safe_exa_search],
        model=llm_model,
    )

    # 4. Main Breakfast Advisor (The Orchestrator)
    breakfast_advisor_guarded = Agent(
        name="breakfast_advisor_guarded_agent",
        instructions="""
        * You are a breakfast advisor. You come up with meal plans for the user based on their preferences.
        * You also calculate the calories for the meal and its ingredients.
        * Based on the breakfast meals and the calories that you get from upstream agents,
        * Create a meal plan for the user. For each meal, give a name, the ingredients, and the calories
        * You only answer questions about food.
        Follow this workflow carefully:
        1) Use the breakfast_planner_tool to plan a a number of healthy breakfast options.
        2) Use the calorie_calculator_tool to calculate the calories for the meal and its ingredients.
        3) Always handoff the breakfast meals and the calories to the Use the Breakfast Price Checker Assistant to add the prices in the last step.
        """,
        tools=[breakfast_planner_tool, calorie_calculator_tool],
        handoff_description="Create a concise breakfast recommendation based on the user's preferences. Use Markdown format.",
        handoffs=[breakfast_price_checker_agent],
        input_guardrails=[food_topic_guardrail],
        model=llm_model,
    )

    return {
        "nutrition_agent": calorie_agent_with_search_guarded,
        "breakfast_advisor": breakfast_advisor_guarded,
        "mcp_server": exa_search_mcp
    }