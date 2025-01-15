import google.generativeai as genai
import os
from dotenv import load_dotenv

import json
import dataclasses
import typing_extensions as typing
from markdown import markdown

load_dotenv()
api_key = os.getenv('api_key')
genai.configure(api_key=api_key)

def set_model(model_name,system_prompt):
  return_model = genai.GenerativeModel( model_name=model_name,
                                       system_instruction=system_prompt)
  return return_model

def email_summary(mail):
    system_instruction = """ From the email please extract out the following using this JSON schema:

    Subject = {"Subject" : str}
    Sender = {"Sender" : str}
    Recipients: {"Recipients": str}
    Date_Time: {"Date/time": datetime}
    Main_Purpose: {"Main Purpose": str}
    Key_Points_Discussed: {"Key Points": str}
    Action_Items_and_Deadlines: {"Deadlines": str}
    Attachments_Links: {"Attachment": str}
    Overall_Tone: {"Tone": str}
    Summary: {"Summary": str}
    Return: list[Subject], list[Sender], list[Recipients], list[Date_Time], list[Main_Purpose], list[Key_Points_Discussed], list[Action_Items_and_Deadlines], list[Attachments_Links], list[Overall_Tone], list[Summary]

    """

    flash_model = set_model('models/gemini-1.5-flash-002',system_instruction)

    flash_model_response = flash_model.generate_content(mail)
    response = markdown(flash_model_response.text)
    return response


mail = """
Email Thread
Subject: Project Update and Next Steps for Q1 Launch
From: Sarah Lee sarah.lee@company.com
To: Team Alpha team.alpha@company.com
Date: January 10, 2025, 9:15 AM

Hi Team,

Hope this email finds you well! I wanted to share an update on the Q1 product launch timeline.

Updates:

The design team has finalized the mockups.
Development is progressing well, but we may need an extra week to complete testing.
Action Items:

Marketing (John): Prepare the draft for the launch email by January 15.
Design (Emily): Upload the final assets to the shared drive by January 12.
Development (Alex): Confirm testing completion by January 20.
Let me know if there are any blockers.

Best regards,
Sarah

From: Emily Chen emily.chen@company.com
To: Sarah Lee sarah.lee@company.com, Team Alpha team.alpha@company.com
Date: January 10, 2025, 10:05 AM

Hi Sarah,

Thanks for the update. The design assets will be uploaded by EOD tomorrow (January 12).

@John – could you also check the brand guidelines to ensure alignment for the launch email?

Best,
Emily

From: John Doe john.doe@company.com
To: Sarah Lee sarah.lee@company.com, Team Alpha team.alpha@company.com
Date: January 10, 2025, 11:30 AM

Hi Team,

Got it. I’ll share a draft of the launch email by January 15. I’ll also cross-check the brand guidelines before finalizing.

Quick note: Can we get an update on the testing status during tomorrow’s standup?

Cheers,
John

From: Alex Kim alex.kim@company.com
To: Sarah Lee sarah.lee@company.com, Team Alpha team.alpha@company.com
Date: January 10, 2025, 2:45 PM

Hi all,

Testing is on track, and I’ll confirm by January 20 as planned. Let me know if there’s anything else you need.

Thanks,
Alex
"""

system_instruction = """ From the email please extract out the following using this JSON schema:

Subject = {"Subject" : str}
Sender = {"Sender" : str}
Recipients: {"Recipients": str}
Date_Time: {"Date/time": datetime}
Main_Purpose: {"Main Purpose": str}
Key_Points_Discussed: {"Key Points": str}
Action_Items_and_Deadlines: {"Deadlines": str}
Attachments_Links: {"Attachment": str}
Overall_Tone: {"Tone": str}
Summary: {"Summary": str}
Return: list[Subject], list[Sender], list[Recipients], list[Date_Time], list[Main_Purpose], list[Key_Points_Discussed], list[Action_Items_and_Deadlines], list[Attachments_Links], list[Overall_Tone], list[Summary]

"""

flash_model = set_model('models/gemini-1.5-flash-002',system_instruction)

flash_model_response = flash_model.generate_content(mail)
response = markdown(flash_model_response.text)
print(response)
