import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from agents import function_tool

SCOPES = ['https://www.googleapis.com/auth/presentations']

def get_slides_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('slides', 'v1', credentials=creds)

@function_tool
def generate_breakfast_deck(plan_title: str, text_summary: str, chart_data_json: str) -> str:
    """
    Creates a populated Google Slides presentation with a Title and a Details slide.
    """
    try:
        service = get_slides_service()
        
        # 1. Create the Presentation
        presentation = service.presentations().create(body={'title': f"AI Breakfast: {plan_title}"}).execute()
        presentation_id = presentation.get('presentationId')

        # 2. Parse the chart data to make it readable
        try:
            data = json.loads(chart_data_json)
            meal_list = "\n".join([f"• {m['food_item']}: {m['calories']} kcal" for m in data])
        except:
            meal_list = chart_data_json # Fallback if not valid JSON

        # 3. Define the Batch Update Requests
        requests = [
            # --- STEP A: Update the default Title Slide (Slide 0) ---
            # Most new presentations start with one default slide (ID 'p')
            {
                'insertText': {
                    'objectId': 'p', # 'p' is usually the first slide, but let's use replaceAllText for safety
                    'text': plan_title,
                    'insertionIndex': 0
                }
            },
            # --- STEP B: Create a New Slide with Specific Mappings ---
            {
                'createSlide': {
                    'objectId': 'summary_page_1',
                    'insertionIndex': '1',
                    'slideLayoutReference': {'predefinedLayout': 'TITLE_AND_BODY'},
                    'placeholderIdMappings': [
                        {
                            'layoutPlaceholder': {'type': 'TITLE', 'index': 0},
                            'objectId': 'title_shape_1' # We name it so we can find it!
                        },
                        {
                            'layoutPlaceholder': {'type': 'BODY', 'index': 0},
                            'objectId': 'body_shape_1'
                        }
                    ]
                }
            },
            # --- STEP C: Insert Text into the named shapes ---
            {
                'insertText': {
                    'objectId': 'title_shape_1',
                    'text': 'Your Nutritional Plan'
                }
            },
            {
                'insertText': {
                    'objectId': 'body_shape_1',
                    'text': f"{text_summary}\n\nCALORIE BREAKDOWN:\n{meal_list}"
                }
            }
        ]

        # 4. EXECUTE THE UPDATE (This was the missing step!)
        service.presentations().batchUpdate(
            presentationId=presentation_id, 
            body={'requests': requests}
        ).execute()

        slide_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
        return f"SUCCESS! Your deck is ready at: {slide_url}"

    except Exception as e:
        return f"Failed to populate slides: {str(e)}"