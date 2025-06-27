"""
Processing Date Estimator

This script analyzes historical processing date data to estimate when a specific eligibility date
will be reached. It uses linear regression to project processing date progression and provides
visual analysis with matplotlib charts.

Features:
- Linear regression analysis of processing date trends
- Interactive matplotlib visualization with scatter plots and projections
- Automatic date parsing and conversion
- Projection line showing estimated future processing dates
- Visual markers for eligibility date and estimated reach date
- Console output with estimated date

Dependencies:
- pandas: Data manipulation and analysis
- matplotlib: Data visualization and plotting
- numpy: Numerical computations and polynomial fitting
- datetime: Date handling (standard library)
- json: JSON file reading (standard library)

Usage:
    uv run python pyscripts/estimator.py
    or
    poetry run python pyscripts/estimator.py

The script reads data from data/processing_data.json and projects when a target eligibility date
will be reached based on the current processing rate.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import json


def load_data_from_json(file_path: str = "data/processing_data.json") -> tuple[dict[str, list[str]] | None, dict[str, list[str]] | None, str | None]:
    """Load data from JSON file."""
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        actual_data = json_data["data"]
        speculative_data = json_data.get("speculative_data", None)
        eligibility_date_str = json_data["eligibility_date_str"]
        return actual_data, speculative_data, eligibility_date_str
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None, None, None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}: {e}")
        return None, None, None


def estimate_processing_date(actual_data: dict[str, list[str]], speculative_data: dict[str, list[str]] | None, eligibility_date_str: str = "1 March 2024") -> None:
    df = pd.DataFrame(actual_data)

    df["Recorded Date"] = pd.to_datetime(df["Recorded Date"], format="%B %Y")
    df["Current Processing Date"] = pd.to_datetime(df["Current Processing Date"], format="%d %b %Y")

    recorded_ordinal = df["Recorded Date"].map(datetime.toordinal)
    processing_ordinal = df["Current Processing Date"].map(datetime.toordinal)

    coefficients = np.polyfit(recorded_ordinal, processing_ordinal, 1)
    poly = np.poly1d(coefficients)

    # Initialize speculative variables
    speculative_df = None
    speculative_coefficients = None
    speculative_poly = None
    speculative_estimated_date = None

    # Process speculative data if available
    if speculative_data:
        speculative_df = pd.DataFrame(speculative_data)
        speculative_df["Recorded Date"] = pd.to_datetime(speculative_df["Recorded Date"], format="%B %Y")
        speculative_df["Current Processing Date"] = pd.to_datetime(speculative_df["Current Processing Date"], format="%d %b %Y")
        
        speculative_recorded_ordinal = speculative_df["Recorded Date"].map(datetime.toordinal)
        speculative_processing_ordinal = speculative_df["Current Processing Date"].map(datetime.toordinal)
        
        speculative_coefficients = np.polyfit(speculative_recorded_ordinal, speculative_processing_ordinal, 1)
        speculative_poly = np.poly1d(speculative_coefficients)

    eligibility_date = pd.to_datetime(eligibility_date_str)
    eligibility_ordinal = eligibility_date.toordinal()

    estimated_recorded_ordinal = (eligibility_ordinal - coefficients[1]) / coefficients[0]
    estimated_date = datetime.fromordinal(int(estimated_recorded_ordinal))
    
    # Calculate speculative estimate if data is available
    if speculative_data and speculative_coefficients is not None:
        speculative_estimated_recorded_ordinal = (eligibility_ordinal - speculative_coefficients[1]) / speculative_coefficients[0]
        speculative_estimated_date = datetime.fromordinal(int(speculative_estimated_recorded_ordinal))

    plt.figure(figsize=(12, 8))
    
    # Plot the actual data points
    plt.scatter(df["Recorded Date"].to_numpy(), df["Current Processing Date"].to_numpy(), color='blue', s=50, label="Actual Data Points")
    
    # Plot the trend line through actual data
    plt.plot(df["Recorded Date"].to_numpy(), df["Current Processing Date"].to_numpy(), color='blue', linestyle='dashed', alpha=0.7)

    # Create a reasonable projection range (extend 2 years beyond the last recorded date)
    last_recorded_date = df["Recorded Date"].max()
    projection_end = last_recorded_date + pd.DateOffset(years=2)
    
    # Create projection dates
    projection_dates = pd.date_range(start=df["Recorded Date"].min(), end=projection_end, freq='ME')
    projection_processing_dates = pd.to_datetime([datetime.fromordinal(int(poly(d.toordinal()))) for d in projection_dates])
    
    # Plot the actual projection line
    plt.plot(projection_dates.values, projection_processing_dates.values, color='red', linestyle='-', linewidth=2, label="Actual Projection")
    
    # Plot speculative data and projection if available
    if speculative_data and speculative_df is not None and speculative_poly is not None:
        plt.scatter(speculative_df["Recorded Date"].to_numpy(), speculative_df["Current Processing Date"].to_numpy(), 
                    color='orange', s=30, alpha=0.6, label="Speculative Data Points")
        
        # Create speculative projection
        speculative_projection_processing_dates = pd.to_datetime([datetime.fromordinal(int(speculative_poly(d.toordinal()))) for d in projection_dates])
        plt.plot(projection_dates.values, speculative_projection_processing_dates.values, color='orange', linestyle='-', linewidth=2, label="Speculative Projection")

    # Add horizontal line for eligibility date
    plt.axhline(y=float(mdates.date2num(eligibility_date)), color='green', linestyle='--', linewidth=2, label=f"Eligibility Date ({eligibility_date.strftime('%d %b %Y')})")
    
    # Add vertical lines for estimated dates
    plt.axvline(x=float(mdates.date2num(estimated_date)), color='red', linestyle='--', linewidth=2, label=f"Actual Estimate: {estimated_date.strftime('%B %Y')}")
    
    if speculative_data and speculative_estimated_date is not None:
        plt.axvline(x=float(mdates.date2num(speculative_estimated_date)), color='orange', linestyle='--', linewidth=2, label=f"Speculative Estimate: {speculative_estimated_date.strftime('%B %Y')}")

    # Format the axes
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gca().yaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # Show every 3 months
    plt.gca().yaxis.set_major_locator(mdates.MonthLocator(interval=2))  # Show every 2 months
    
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels

    plt.xlabel("Recorded Date", fontsize=12)
    plt.ylabel("Current Processing Date", fontsize=12)
    plt.title("Processing Date Progression and Estimates", fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Set reasonable axis limits
    plt.xlim(df["Recorded Date"].min() - pd.DateOffset(months=1), projection_end)
    plt.ylim(df["Current Processing Date"].min() - pd.DateOffset(months=1), 
             max(eligibility_date, df["Current Processing Date"].max()) + pd.DateOffset(months=1))
    
    plt.tight_layout()
    plt.show()

    print(f"Actual estimate: {estimated_date.strftime('%B %Y')}")
    if speculative_data and speculative_estimated_date is not None:
        print(f"Speculative estimate: {speculative_estimated_date.strftime('%B %Y')}")
    print(f"Data spans from {df['Recorded Date'].min().strftime('%B %Y')} to {df['Recorded Date'].max().strftime('%B %Y')}")
    print(f"Processing dates span from {df['Current Processing Date'].min().strftime('%d %b %Y')} to {df['Current Processing Date'].max().strftime('%d %b %Y')}")


def main() -> None:
    """Main function to run the estimator."""
    actual_data, speculative_data, eligibility_date_str = load_data_from_json()
    
    if actual_data is None or eligibility_date_str is None:
        print("Failed to load data. Please check the JSON file.")
        return
    
    print(f"Loaded data with eligibility date: {eligibility_date_str}")
    if speculative_data:
        print("Speculative data found and will be included in analysis.")
    else:
        print("No speculative data found. Only actual data will be analyzed.")
    
    estimate_processing_date(actual_data, speculative_data, eligibility_date_str)


if __name__ == "__main__":
    main()
