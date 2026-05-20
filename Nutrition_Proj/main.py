from dotenv import load_dotenv
load_dotenv()

import asyncio
from agents import Runner
from agent_factory import build_agents

async def main():
    print("Initializing agents...")
    agents = build_agents()
    
    advisor_agent = agents["breakfast_advisor"]
    # mcp_server = agents["mcp_server"]
    
    # CONNECT THE SERVER! 
    # await mcp_server.connect()
    
    user_input = "I need a high-protein, quick breakfast for busy mornings."
    print(f"Running advisor for input: '{user_input}'\n")
    
    try:
        result = await Runner.run(advisor_agent, user_input)
        print("--- Final Output ---")
        print(result.final_output)
        
    except Exception as e:
        # This will catch the 429 Rate Limit error cleanly!
        print(f"\n[Agent Error]: {e}")
        
    # finally:
    #     print("\nCleaning up network connections...")
    #     try:
    #         if hasattr(mcp_server, 'close'):
    #             await mcp_server.close()
    #         elif hasattr(mcp_server, 'disconnect'):
    #             await mcp_server.disconnect()
            
    #         # THE MAGIC SLEEP: Gives Python time to actually hang up the phone
    #         await asyncio.sleep(0.5) 
    #         print("Cleanup successful.")
    #     except Exception as cleanup_error:
    #         pass # Suppress ugly shutdown errors

if __name__ == "__main__":
    asyncio.run(main())