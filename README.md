# Restaurant Dashboard

A restaurant dashboard for servers and front-of-house staff to manage reservations, analyze diner data, and leverage AI for personalized follow-ups.

## Video Demo

[![Watch the video](https://img.youtube.com/vi/uQ1ctilWnkk/0.jpg)](https://www.youtube.com/watch?v=uQ1ctilWnkk)

---

## Structure

The application has been organized into modular components for better readability and maintenance:

#### 1. `data_processor.py`
- Handles all data loading and processing functions
- Contains functions to load, bucket, and transform reservation data
- Creates specialized dataframes for different table views

#### 2. `streamlit_ui_components.py`
- Manages UI elements and display functions
- Handles statistics and table output 
- Creates the audio upload section with consolidated transcription and analysis

#### 3. `ai_integrations.py`
- Integrates with Cohere and OpenAI APIs
- Analyzes diner data to identify follow-up needs (Smart Inbox)
- Processes audio transcriptions of morning huddles
- Handles AI-related operations with parallel processing

#### 4. `prompts.py`
- Contains all AI prompts used for Cohere and OpenAI interactions for better maintainability
- Organizes prompts in a structured, easy-to-update format

#### 5. `restaurant_dashboard_app.py`
- Main entry point that integrates all modules
- Orchestrates the application flow
- Manages session state and caching

## Features

- **Reservation Management**: View and filter reservations by date range
- **Smart Inbox**: AI-powered follow-up recommendations
- **Audio Transcription**: Convert morning huddle recordings to text
- **Data Analysis**: Statistics and visualizations for each date bucket
- **Specialized Views**: Dietary restrictions and special occasions tables

## Running the Application
1. Create and activate the conda environment:
```bash
conda env create -f environment.yaml
conda activate restaurant-dashboard
```

2. Run the Streamlit app:
```bash
streamlit run restaurant_dashboard/restaurant_dashboard_app.py
```

## API Keys

The application uses two external APIs:

1. **Cohere API**: For analyzing diner data and transcripts
   - Set with environment variable `COHERE_API_KEY`

2. **OpenAI API**: For audio transcription
   - Set with environment variable `OPENAI_API_KEY`
