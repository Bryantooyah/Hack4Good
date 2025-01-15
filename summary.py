import google.generativeai as genai
import os
from dotenv import load_dotenv

from IPython.display import display
from IPython.display import Markdown

import json
import dataclasses
import typing_extensions as typing

load_dotenv()
api_key = os.getenv('api_key')
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash-latest", generation_config={"response_mime_type": "application/json"})
