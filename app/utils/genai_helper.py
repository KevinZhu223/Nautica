import os
import tempfile
import requests
from google import genai
from google.genai import types
from app.config.settings import Settings

settings = Settings()

def send_project_images_to_genai(project, prompt="placeholder"):
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
    )

    uploaded_files = []

    for image_url in project.pictures:
        try:

            response = requests.get(image_url)
            response.raise_for_status()
            

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(response.content)
                temp_file_path = tmp.name

            file_obj = client.files.upload(file=temp_file_path)
            uploaded_files.append(file_obj)
            
            os.remove(temp_file_path)
        except Exception as e:
            print(f"Failed to process image {image_url}: {e}")
            continue

    if not uploaded_files:
        raise Exception("No images were successfully uploaded to GenAI.")

    contents = [
         types.Content(
             role="user",
             parts=[
                 types.Part.from_uri(
                     file_uri=uploaded_files[0].uri,
                     mime_type=uploaded_files[0].mime_type,
                 ),
             ],
         ),
         types.Content(
             role="user",
             parts=[
                 types.Part.from_text(
                     text=prompt,
                 ),
             ],
         ),
    ]
    
    # Optional tools for the generation call (example: Google Search)
    tools = [types.Tool(google_search=types.GoogleSearch())]
    
    generate_content_config = types.GenerateContentConfig(
         temperature=1,
         top_p=0.95,
         top_k=64,
         max_output_tokens=8192,
         tools=tools,
         response_mime_type="text/plain",
    )

    output = ""
    # Stream the response from the GenAI model
    for chunk in client.models.generate_content_stream(
         model="gemini-2.0-pro-exp-02-05",
         contents=contents,
         config=generate_content_config,
    ):
         output += chunk.text
    return output
