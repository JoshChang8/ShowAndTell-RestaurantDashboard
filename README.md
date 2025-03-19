# Restaurant Dashboard

A Streamlit-based dashboard for managing restaurant reservations, analyzing diner data, and identifying follow-up opportunities using AI.

## Structure

The application has been organized into modular components for better readability and maintenance:

### 1. `data_processor.py`
- Handles all data loading and processing functions
- Contains functions to load, bucket, and transform reservation data
- Creates specialized dataframes for different table views

### 2. `streamlit_ui_components.py`
- Manages the UI elements and display functions
- Implements expandable tables with VIP highlighting
- Handles statistics display with accurate calculation of stats
- Creates the audio upload section with consolidated transcription and analysis

### 3. `ai_integrations.py`
- Integrates with Cohere and OpenAI APIs
- Analyzes diner data to identify follow-up needs
- Processes audio transcriptions of morning huddles
- Handles AI-related operations with parallel processing

### 4. `prompts.py`
- Contains all AI prompts used for Cohere and OpenAI interactions
- Separates prompt text from code logic for better maintainability
- Organizes prompts in a structured, easy-to-update format

### 5. `restaurant_dashboard_app.py`
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
