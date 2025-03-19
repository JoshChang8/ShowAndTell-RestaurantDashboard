import streamlit as st
from data_processor import (
    load_data, 
    create_master_table, 
    create_dietary_table, 
    create_special_occasions_table
)
from streamlit_ui_components import (
    setup_page_config, 
    display_stats, 
    display_table_with_expander,
    display_audio_section
)
from ai_integrations import (
    analyze_diners_for_followup,
    transcribe_audio,
    analyze_huddle_transcript
)

def main():
    """Main application entry point."""
    setup_page_config()
    
    st.title("Morning Huddle Server Dashboard 🧑‍🍳")
    st.markdown("View and analyze Diner Reservation data by date range.")
    
    # Add sidebar for Smart Inbox
    with st.sidebar:
        st.header("Smart Inbox 📬")
        st.write("Diners Requiring a Follow-up")
        st.write("List of diners who need a follow-up based on specific questions, requests, or concerns:")
        st.divider()
        # Create a placeholder for follow-up content
        followup_placeholder = st.empty()
    
    # Initialize session state for expanded tables if not already present
    if 'all_reservations_expanded' not in st.session_state:
        st.session_state.all_reservations_expanded = False
    if 'dietary_restrictions_expanded' not in st.session_state:
        st.session_state.dietary_restrictions_expanded = False
    if 'special_occasions_expanded' not in st.session_state:
        st.session_state.special_occasions_expanded = False
        
    # Initialize session state for Smart Inbox cache
    if 'smart_inbox_cache' not in st.session_state:
        st.session_state.smart_inbox_cache = {}
    if 'last_selected_bucket' not in st.session_state:
        st.session_state.last_selected_bucket = None
    
    # Initialize session state for audio analysis
    if 'audio_transcription' not in st.session_state:
        st.session_state.audio_transcription = None
    if 'audio_analysis' not in st.session_state:
        st.session_state.audio_analysis = None
    
    try:
        # Load the date-bucketed data
        buckets = load_data()
        
        if not buckets:
            st.error("No reservation data available. Please check the data files.")
            return
        
        # Bucket selection
        bucket_options = list(buckets.keys())
        selected_bucket = st.selectbox(
            "Select a date range:",
            bucket_options,
            help="Choose a time period to view reservations"
        )
        
        # Process data for the selected bucket
        diners_in_bucket = buckets[selected_bucket]
        
        # Create master dataframe
        master_df = create_master_table(diners_in_bucket)
        
        if master_df.empty:
            st.info("No reservations found for this time period.")
            return
        
        # Display statistics
        display_stats(master_df, selected_bucket)
        
        # Add a divider between sections
        st.markdown("---")
        
        # Add Morning Huddle Audio Transcription section with all components in a single expander
        # We pass the transcribe and analyze functions directly to the display function
        display_audio_section(transcribe_audio, analyze_huddle_transcript)
        
        # Add a divider after the audio analysis section
        st.markdown("---")
        
        # Display master table
        display_table_with_expander(
            master_df, 
            "All Reservations 🍽️", 
            "No reservations found for this time period."
        )
        
        # Add a divider between tables
        st.markdown("---")
        
        # Create and display dietary restrictions table
        dietary_df = create_dietary_table(master_df)
        display_table_with_expander(
            dietary_df, 
            "Dietary Restrictions 🚫", 
            "No diners with dietary restrictions found for this time period."
        )
        
        # Add a divider between tables
        st.markdown("---")
        
        # Create and display special occasions table
        occasions_df = create_special_occasions_table(master_df)
        display_table_with_expander(
            occasions_df, 
            "Special Occasions 🎉", 
            "No diners with special occasions found for this time period."
        )
        
        # Process data for Smart Inbox in the sidebar after tables are displayed
        # Only regenerate analysis if the bucket has changed
        with st.sidebar:
            # Check if we need to regenerate the analysis
            if selected_bucket != st.session_state.last_selected_bucket or selected_bucket not in st.session_state.smart_inbox_cache:
                with st.spinner("Analyzing diners for follow-up..."):
                    # Generate new analysis
                    followup_text = analyze_diners_for_followup(diners_in_bucket)
                    # Cache the results
                    st.session_state.smart_inbox_cache[selected_bucket] = followup_text
                    # Update the last selected bucket
                    st.session_state.last_selected_bucket = selected_bucket
            else:
                # Use cached results
                followup_text = st.session_state.smart_inbox_cache[selected_bucket]
                
            # Update the placeholder with the results
            with followup_placeholder.container():
                st.markdown(followup_text)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
