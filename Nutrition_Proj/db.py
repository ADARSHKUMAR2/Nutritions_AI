import os
from pathlib import Path
import chromadb
from agents import function_tool
from exa_py import Exa
from langsmith import traceable

def get_nutrition_db():
    """Initializes and returns the ChromaDB collection."""
    chroma_path = Path(__file__).parent / "chroma" 
    chroma_client = chromadb.PersistentClient(path=str(chroma_path))
    
    # Use get_or_create to prevent crash if it doesn't exist yet
    return chroma_client.get_or_create_collection(name="nutrition_db")

# Initialize at module level
nutrition_db = get_nutrition_db()

# Check that this exact block exists in db.py!
@function_tool
def calorie_lookup_tool(query: str, max_results: int = 3) -> str:
    results = nutrition_db.query(query_texts=[query], n_results=max_results)
    if not results["documents"][0]:
        return f"No nutrition information found for: {query}"
        
    formatted_results = []
    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        food_item = metadata["food_item"].title()
        calories = metadata["calories_per_100g"]
        category = metadata["food_category"].title()
        formatted_results.append(
            f"{food_item} ({category}): {calories} calories per 100g"
        )
    return "Nutrition Information:\n" + "\n".join(formatted_results)

@function_tool
def safe_exa_search(query: str) -> str:
    """Use this tool to search the internet for prices or nutrition info safely."""
    try:
        exa = Exa(api_key=os.environ.get("EXA_API_KEY"))
        # Ask Exa for a max of 1 result, and physically limit the text it returns
        result = exa.search_and_contents(
            query,
            num_results=1,
            text={"max_characters": 1000} # <-- THE TOKEN SAVER!
        )
        
        # Turn the result into a simple string
        if result and result.results:
            first_result = result.results[0]
            return f"Title: {first_result.title}\nText: {first_result.text}"
        return "No results found."
        
    except Exception as e:
        return f"Search failed: {e}"