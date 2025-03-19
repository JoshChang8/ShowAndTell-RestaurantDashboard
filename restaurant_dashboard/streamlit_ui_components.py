import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Restaurant Reservation Dashboard",
        page_icon="🍽️",
        layout="wide"
    )

def display_stats(df: pd.DataFrame, bucket: str):
    """Display key statistics about the current bucket."""
    st.header(f"Reservation Overview {bucket}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total number of reservations is the number of rows in the dataframe
        total_reservations = len(df)
        st.metric("Total Reservations", total_reservations)
    
    with col2:
        # Total number of guests is the sum of the Party Size column
        # Convert to numeric first to handle any non-numeric values
        df['Party Size'] = pd.to_numeric(df['Party Size'], errors='coerce')
        total_party_size = int(df['Party Size'].sum())
        st.metric("Total Guests", total_party_size)
    
    with col3:
        # Count diners with non-empty dietary information
        total_dietary = df[df['Dietary Information'].astype(str).str.strip() != ''].shape[0]
        st.metric("Diners with Dietary Preferences", total_dietary)
    
    with col4:
        # Count diners with non-empty special occasions
        total_special_occasions = df[df['Special Occasion'].astype(str).str.strip() != ''].shape[0]
        st.metric("Total Special Occasions", total_special_occasions)

def display_table_with_expander(df: pd.DataFrame, title: str, empty_message: str = "No data found for this time period."):
    """
    Display a table with an expand/collapse button to show all rows or just the first 5.
    Format columns with different widths based on content type.
    """
    if df.empty:
        st.info(empty_message)
        return
    
    # Initialize session state for this table if not already present
    table_id = title.lower().replace(" ", "_")
    if f'{table_id}_expanded' not in st.session_state:
        st.session_state[f'{table_id}_expanded'] = False
    
    # Create a container for the table
    table_container = st.container()
    
    with table_container:
        st.subheader(title)
        
        # Display either all rows or just the first 5
        display_df = df if st.session_state[f'{table_id}_expanded'] else df.head(5)
        
        # Format any VIP customers with a highlight (soft orange #FFE5B4)
        # This assumes there's a "VIP" column or we're identifying VIPs some other way
        # For demonstration, we'll check if "VIP" is in the Additional Information field
        if "Additional Information" in display_df.columns:
            def highlight_vip(row):
                if isinstance(row["Additional Information"], str) and "VIP" in row["Additional Information"].upper():
                    return ['background-color: #FFE5B4'] * len(row)
                return [''] * len(row)
            
            styled_df = display_df.style.apply(highlight_vip, axis=1)
        else:
            styled_df = display_df
            
        # Configure column widths
        column_config = {}
        
        # Configure columns with appropriate widths
        for col in display_df.columns:
            if col == "Additional Information":
                # Give Additional Information column all remaining space
                column_config[col] = st.column_config.TextColumn(
                    col,
                    width="large",  # Largest available preset size
                    help="Additional notes and requests"
                )
            elif col == "Party Size":
                # Make Party Size column narrow and left-aligned
                column_config[col] = st.column_config.TextColumn(
                    col,
                    width="small",
                    help="Number of guests"
                )
            elif col == "Date":
                # Date column with consistent width
                column_config[col] = st.column_config.DateColumn(
                    col,
                    width="small",
                    format="YYYY-MM-DD"
                )
            elif col in ["Dietary Information", "Special Occasion"]:
                # Medium width for these columns
                column_config[col] = st.column_config.TextColumn(
                    col,
                    width="medium"
                )
            elif col == "Past Visit Experience":
                # Format according to user preference (rating on first line, notes on second)
                column_config[col] = st.column_config.TextColumn(
                    col,
                    width="medium",
                    help="Customer's previous experience"
                )
            else:
                # Other columns (like Name) get small width
                column_config[col] = st.column_config.TextColumn(
                    col,
                    width="small"
                )
        
        # Display the dataframe with column configuration
        st.dataframe(styled_df, use_container_width=True, hide_index=True, column_config=column_config)
        
        # Add expand/collapse button if there are more than 5 rows
        if len(df) > 5:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                button_label = "Collapse Table" if st.session_state[f'{table_id}_expanded'] else f"Show All {title}"
                if st.button(button_label, key=f"{table_id}_expand_button"):
                    st.session_state[f'{table_id}_expanded'] = not st.session_state[f'{table_id}_expanded']
                    st.experimental_rerun()

def display_audio_section(transcribe_func, analyze_func):
    """
    Display the morning huddle audio transcription section with all components in a single expander.
    
    Args:
        transcribe_func: Function to transcribe audio
        analyze_func: Function to analyze transcript
        
    Returns:
        None
    """
    st.header("Morning Huddle Transcription")
    
    # Create a single expander for all audio transcription functionality
    with st.expander("Morning Huddle Details", expanded=False):
        st.write("Upload an audio recording of your morning huddle to get insights and action items.")
        
        # File upload
        audio_file = st.file_uploader("Upload morning huddle audio recording", type=["mp3", "wav", "m4a"])
        
        # Transcribe & Analyze button below the dropbox
        if st.button("Transcribe & Analyze", disabled=audio_file is None):
            with st.spinner("Transcribing audio..."):
                # Transcribe the audio
                transcription = transcribe_func(audio_file)
                st.session_state.audio_transcription = transcription
                
                # Analyze the transcription
                with st.spinner("Analyzing transcription..."):
                    analysis = analyze_func(transcription)
                    st.session_state.audio_analysis = analysis
        
        # Display transcription and analysis if available
        if ('audio_transcription' in st.session_state and 
            st.session_state.audio_transcription and 
            'audio_analysis' in st.session_state and 
            st.session_state.audio_analysis):
            
            st.markdown("### Transcription")
            st.write(st.session_state.audio_transcription)
            
            # Handle errors in analysis
            if "error" in st.session_state.audio_analysis:
                st.error(st.session_state.audio_analysis["error"])
                if "raw_text" in st.session_state.audio_analysis:
                    st.code(st.session_state.audio_analysis["raw_text"])
            else:
                analysis = st.session_state.audio_analysis
                
                # Display Meeting Summary
                st.markdown("### Meeting Summary")
                st.write(analysis.get("summary", "No summary available"))
                
                # Display Action Items
                st.markdown("### Action Items")
                items = analysis.get("action_items", [])
                if items:
                    for item in items:
                        st.write(f"• {item}")
                else:
                    st.write("No action items identified from the meeting.")
