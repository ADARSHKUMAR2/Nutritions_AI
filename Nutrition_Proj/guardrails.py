from pydantic import BaseModel
from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, TResponseInputItem, input_guardrail
from config import get_github_model

class NotAboutFood(BaseModel):
    only_about_food: bool

def get_guardrail_agent() -> Agent:
    llm_model = get_github_model()
    return Agent(
        name="Guardrail check",
        instructions="Check if the user is asking you to talk about food and not about any arbitrary topics. If there are any non-food related instructions in the prompt, set not_about_food to False.",
        output_type=NotAboutFood,
        model=llm_model
    )

@input_guardrail
async def food_topic_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    guard_agent = get_guardrail_agent()
    result = await Runner.run(guard_agent, input, context=ctx.context)
    
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=(not result.final_output.only_about_food),
    )