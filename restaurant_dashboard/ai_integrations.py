import cohere
import openai
import json
import os
import tempfile
import time
from typing import Dict, List, Any
import streamlit as st
from joblib import Parallel, delayed
import joblib
from datetime import datetime
from dotenv import load_dotenv

# Import prompts from prompts.py
from prompts import HUDDLE_ANALYSIS_PROMPT, DINER_FOLLOWUP_PREFIX, DINER_FOLLOWUP_SUFFIX

# Define types for clarity
Diner = Dict[str, Any]

def get_cohere_api_key() -> str:
    """Get the Cohere API key."""
    # First try environment variable (best practice)
    load_dotenv()
    api_key = os.getenv('COHERE_API_KEY')
    
    # If not found, fall back to hardcoded key (not recommended for production)
    if not api_key:
        api_key = "REPLACE WITH ACTUAL KEY"  # Replace with your actual key
    return api_key

def get_openai_api_key():
    """
    Get the OpenAI API key.
    
    First checks for the OPENAI_API_KEY environment variable.
    If not found, falls back to a hardcoded key.
    
    Returns:
        str: The OpenAI API key
    """
    # First, try to get the API key from the environment variable
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    # If not found, use a hardcoded key (replace with your key)
    # NOTE: It's better to use environment variables in production!
    if not api_key:
        api_key = "REPLACE WITH ACTUAL KEY"  # Replace with your actual key
    return api_key

def transcribe_audio(audio_file):
    """
    Transcribe audio file using OpenAI's Whisper model.
    
    Args:
        audio_file: Uploaded audio file from Streamlit
        
    Returns:
        str: Transcribed text
    """
    try:
        api_key = get_openai_api_key()
        openai.api_key = api_key
        
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Transcribe using Whisper
        client = openai.OpenAI(api_key=api_key)
        with open(tmp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Clean up the temporary file
        os.unlink(tmp_file_path)
        
        return transcript.text
    
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"

def analyze_huddle_transcript(transcript):
    """
    Analyze the transcribed morning huddle text using Cohere API.
    
    Args:
        transcript: Transcribed text from the morning huddle
        
    Returns:
        dict: Analysis results with summary and action items
    """
    try:
        # Get Cohere API key
        api_key = get_cohere_api_key()
        
        if not api_key:
            return {"error": "Cohere API key not found."}
        
        # Initialize Cohere client
        co = cohere.Client(api_key)
        
        # Use the prompt from prompts.py, formatting it with the transcript
        prompt = HUDDLE_ANALYSIS_PROMPT.format(transcript=transcript)
        
        # Generate analysis
        response = co.generate(
            prompt=prompt,
            max_tokens=750,
            temperature=0.7,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        
        # Parse the response
        try:
            analysis = json.loads(response.generations[0].text.strip())
            return analysis
        except json.JSONDecodeError:
            return {"error": "Could not parse response as JSON.", "raw_text": response.generations[0].text.strip()}
    
    except Exception as e:
        return {"error": f"Error analyzing transcript: {str(e)}"}

def process_diner_batch(batch: List[Diner], api_key: str, batch_id: int) -> dict:
    """
    Process a batch of diners using the Cohere API.
    
    Args:
        batch: A small batch of diners (max 5)
        api_key: Cohere API key
        batch_id: ID of the batch for tracking
        
    Returns:
        Dict: Results including follow-up information
    """
    start_time = time.time()
    try:
        # Initialize Cohere client
        co = cohere.Client(api_key)
        
        # Get names for logging
        batch_names = [diner.get('name', 'Unknown') for diner in batch]
        
        # Use the prompt prefix from prompts.py
        prompt = DINER_FOLLOWUP_PREFIX
        
        # Add diner information to the prompt
        diner_count_with_emails = 0
        for diner in batch:
            # Add basic diner info - name
            name = diner.get('name', 'Unknown')
            prompt += f"\n\n### Diner: {name}"
            
            # Add reservation date - from the first reservation in the reservations list
            if "reservations" in diner and diner["reservations"]:
                reservation_date = diner["reservations"][0].get("date", "Unknown")
                prompt += f"\nReservation Date: {reservation_date}"
            
            # Add emails for follow-up - emails is a list of email objects
            if "emails" in diner and diner["emails"]:
                diner_count_with_emails += 1
                prompt += "\nEmail Inquiries:"
                for email in diner["emails"]:
                    subject = email.get("subject", "No subject")
                    thread = email.get("combined_thread", email.get("content", "No content"))
                    prompt += f"\n- **Subject:** {subject}\n  **Content:** {thread}"
        
        # If no diners have emails, return early
        if diner_count_with_emails == 0:
            return {
                'batch_id': batch_id,
                'batch_size': len(batch),
                'batch_names': batch_names,
                'processing_time': time.time() - start_time,
                'results': []
            }
        
        # Add the instructions suffix from prompts.py
        prompt += DINER_FOLLOWUP_SUFFIX
        
        # Generate response from Cohere
        response = co.generate(
            prompt=prompt,
            max_tokens=750,
            temperature=0.7,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        
        # Get the raw response text
        response_text = response.generations[0].text.strip()
        
        try:
            # Parse the JSON response
            follow_up_diners = json.loads(response_text)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return {
                'batch_id': batch_id,
                'batch_size': len(batch),
                'batch_names': batch_names,
                'processing_time': processing_time,
                'results': follow_up_diners
            }
            
        except json.JSONDecodeError:
            # If there's an error, return empty results with timing info
            processing_time = time.time() - start_time
            return {
                'batch_id': batch_id,
                'batch_size': len(batch),
                'batch_names': batch_names,
                'processing_time': processing_time,
                'error': 'JSON decode error',
                'results': []
            }
            
    except Exception as e:
        # On error, return empty results with timing info
        processing_time = time.time() - start_time
        return {
            'batch_id': batch_id,
            'batch_size': len(batch),
            'batch_names': batch_names if 'batch_names' in locals() else [],
            'processing_time': processing_time,
            'error': str(e),
            'results': []
        }

def analyze_diners_for_followup(diners_list: List[Diner]) -> str:
    """
    Use Cohere API to analyze diners and identify who needs follow-up.
    Processes diners in parallel using joblib for better performance.
    
    Args:
        diners_list: List of diner data from the selected bucket
        
    Returns:
        Formatted text of diners needing follow-up, or error message
    """
    
    # Get API key
    api_key = get_cohere_api_key()
    
    if not api_key:
        return "Error: Cohere API key not found. Please set the COHERE_API_KEY environment variable."
    
    # If there are no diners, return early
    if not diners_list:
        return "No diners found in this time period."
    
    try:
        # Record start time for overall processing
        total_start_time = time.time()
        
        # Split diners into batches of at most 20
        batch_size = 20
        batches = [diners_list[i:i + batch_size] for i in range(0, len(diners_list), batch_size)]
        
        # Use threading backend with appropriate number of jobs
        # This is more compatible with Streamlit than multiprocessing
        n_jobs = min(joblib.cpu_count(), len(batches))
                
        # Create sidebar placeholder for observability info
        with st.sidebar:
            obs_expander = st.expander("Parallelization Metrics", expanded=False)
            with obs_expander:
                st.write(f"**Diner Analysis Info:**")
                st.write(f"Total diners: {len(diners_list)}")
                st.write(f"Batch size: {batch_size}")
                st.write(f"Number of batches: {len(batches)}")
                st.write(f"Parallel jobs: {n_jobs}")
                st.write(f"CPU cores available: {joblib.cpu_count()}")
                st.write(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
                
                # Create a placeholder for progress
                progress_placeholder = st.empty()
                metrics_placeholder = st.empty()
        
        # Process batches in parallel using threading backend
        results = Parallel(n_jobs=n_jobs, backend="threading", verbose=10)(delayed(process_diner_batch)(batch, api_key, i) for i, batch in enumerate(batches))
        
        # Calculate total processing time
        total_processing_time = time.time() - total_start_time
        
        # Update progress with completion
        with obs_expander:
            with progress_placeholder.container():
                st.success(f"Processing complete! Total time: {total_processing_time:.2f} seconds")
            
            # Display batch metrics
            with metrics_placeholder.container():
                st.write("**Batch Processing Times:**")
                for batch_result in results:
                    st.write(f"Batch {batch_result['batch_id']+1}: {batch_result['processing_time']:.2f}s - {len(batch_result['batch_names'])} diners")
        
        # Combine all results
        all_follow_up_diners = []
        for batch_result in results:
            if 'results' in batch_result:
                all_follow_up_diners.extend(batch_result['results'])
        
        # If no diners need follow-up, return message
        if not all_follow_up_diners:
            return "No diners requiring follow-up at this time."
        
        # Format the response as simple text for display in the sidebar
        formatted_output = ""
        for diner in all_follow_up_diners:
            name = diner.get("Name", "Unknown")
            reservation = diner.get("Reservation", "Unknown date")
            reason = diner.get("Reason", "No reason provided")
            
            formatted_output += f"**Name:** {name} ({reservation})\n\n**Reason:** {reason}\n\n---\n"
        
        return formatted_output
        
    except Exception as e:
        return f"Error analyzing diners: {str(e)}"
