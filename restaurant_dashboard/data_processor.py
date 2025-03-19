import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any
import os
from copy import deepcopy

# Define types for clarity
Diner = Dict[str, Any]

def parse_date(date_str: str) -> datetime:
    """Convert 'YYYY-MM-DD' to a datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d")

def get_date_ranges():
    """Define the standard date ranges for bucketing reservations."""
    return [
        {"name": "2024-05 to 2024-09", "start": datetime(2024, 5, 1),  "end": datetime(2024, 9, 30)},
        {"name": "2024-10 to 2024-12", "start": datetime(2024, 10, 1), "end": datetime(2024, 12, 31)},
        {"name": "2025-01 to 2025-02", "start": datetime(2025, 1, 1),  "end": datetime(2025, 2, 28)},
        {"name": "2025-03 to 2025-05", "start": datetime(2025, 3, 1),  "end": datetime(2025, 5, 31)}
    ]

def load_raw_data() -> Dict:
    """Load and parse the JSON data file."""
    # Path to the data file relative to the current directory
    # First try the data folder in the parent directory
    file_path = os.path.join("..", "data", "final-refined-fine-dining-dataset.json")
    
    if not os.path.exists(file_path):
        # If not found, try looking in the current directory
        file_path = os.path.join("data", "final-refined-fine-dining-dataset.json")
    
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {file_path}")
        return {"diners": []}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return {"diners": []}

def bucket_reservations(data: Dict) -> Dict[str, List[Diner]]:
    """
    Process diner data and organize reservations into date-range buckets.
    Returns a dictionary with date range keys and lists of diner data.
    """
    date_ranges = get_date_ranges()
    buckets = {range_info["name"]: [] for range_info in date_ranges}

    for diner in data["diners"]:
        all_reservations = diner.get("reservations", [])

        for date_range in date_ranges:
            bucket_reservations = []

            for reservation in all_reservations:
                res_date = parse_date(reservation["date"])
                if date_range["start"] <= res_date <= date_range["end"]:
                    bucket_reservations.append(reservation)

            if bucket_reservations:
                diner_copy = deepcopy(diner)
                diner_copy["reservations"] = bucket_reservations
                buckets[date_range["name"]].append(diner_copy)

    return buckets

def load_data() -> Dict[str, List[Diner]]:
    """
    Main entry point for loading and processing diner reservation data.
    Returns bucketed reservation data ready for display.
    """
    raw_data = load_raw_data()
    return bucket_reservations(raw_data)

def create_master_table(diners_list: List[Diner]) -> pd.DataFrame:
    """Create a master table of all reservations."""
    rows = []
    
    for diner in diners_list:
        for reservation in diner.get("reservations", []):
            # Create a row for each reservation
            row = {
                "Name": diner.get("name", ""),
                "Date": reservation.get("date", ""),
                "Party Size": reservation.get("number_of_people", ""),
                "Dietary Information": diner.get("dietary_information", ""),
                "Special Occasion": diner.get("special_occasion", ""),
                "Additional Information": diner.get("other_info", "")
            }
            
            # Only add non-empty rows
            if any(value for key, value in row.items() if key != "Name"):
                rows.append(row)
    
    if not rows:
        return pd.DataFrame()
    
    # Create DataFrame and sort by date
    df = pd.DataFrame(rows)
    df = df.sort_values(by="Date")
    
    return df

def create_dietary_table(master_df: pd.DataFrame) -> pd.DataFrame:
    """Create a table of diners with dietary restrictions."""
    # Filter for non-empty dietary information
    dietary_df = master_df[master_df["Dietary Information"].astype(str).str.strip() != ""].copy()
    
    # Select only relevant columns
    if not dietary_df.empty:
        dietary_df = dietary_df[["Name", "Date", "Party Size", "Dietary Information", "Additional Information"]]
    
    return dietary_df

def create_special_occasions_table(master_df: pd.DataFrame) -> pd.DataFrame:
    """Create a table of diners with special occasions."""
    # Filter for non-empty special occasions
    occasions_df = master_df[master_df["Special Occasion"].astype(str).str.strip() != ""].copy()
    
    # Select only relevant columns
    if not occasions_df.empty:
        occasions_df = occasions_df[["Name", "Date", "Party Size", "Special Occasion", "Additional Information"]]
    
    return occasions_df
