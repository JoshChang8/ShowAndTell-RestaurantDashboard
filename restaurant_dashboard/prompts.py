"""
This module contains all the prompts used for AI interactions in the restaurant dashboard app.
Keeping prompts in a separate file improves readability and makes them easier to update.
"""

# Prompt for analyzing morning huddle transcriptions
HUDDLE_ANALYSIS_PROMPT = """
You are an AI assistant for a fine dining restaurant. Analyze the following transcribed morning huddle meeting and extract key information and action items.

Transcription:
{transcript}

Your task is to:
1. Create a concise summary of the morning huddle discussion (max 3 paragraphs)
2. Extract specific items that need attention today (VIP guests, special dietary needs, special occasions)
3. List specific action items for the staff

Format your response as a JSON object with the following structure:
{{"summary": "Summary of the meeting",
"action_items": ["List of action items that need attention (VIP guests, special dietary needs, special occasions)"],}}

Respond ONLY with the JSON. Do not include any explanatory text.
"""

# Prompt prefix for analyzing diners for follow-up
DINER_FOLLOWUP_PREFIX = """
You are an AI assistant for a fine dining restaurant. Analyze the following diners' information and identify which diners need follow-up based on their emails. Focus on diners who have specific questions, requests, or concerns that need addressing.

For each diner that needs follow-up, explain what needs to be addressed.

Here is the diner information:
"""

# Prompt suffix for analyzing diners for follow-up (instructions and format)
DINER_FOLLOWUP_SUFFIX = """

---

## ANALYSIS INSTRUCTIONS

Based on the information above, analyze which diners need follow-up based on their email inquiries.

IMPORTANT: You must respond ONLY with a JSON array. Do not include any explanatory text before or after the JSON.

Each diner requiring follow-up should be included as an object in the array with these exact keys:
- "Name": The diner's full name (string)
- "Reservation": The reservation date in YYYY-MM-DD format (string)
- "Reason": A concise reason why follow-up is needed (string)

### Rules for determining if follow-up is needed:
1. ONLY include diners who have specific questions, requests, or concerns in their emails
2. DO NOT include diners whose inquiries are only about dietary preferences or special occasions
3. If no diners need follow-up, return an empty array: []

### Example of expected response format:
[
  {
    "Name": "Emily Chen",
    "Reservation": "2024-05-20",
    "Reason": "Request to adjust table for an additional guest"
  },
  {
    "Name": "David Martinez",
    "Reservation": "2024-05-20",
    "Reason": "Inquiry about availability of private dining area"
  }
]
"""
