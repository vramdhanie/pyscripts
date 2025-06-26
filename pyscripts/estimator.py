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
import os


def load_data_from_json(file_path: str = "data/processing_data.json"):
    """Load data from JSON file."""
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        return json_data["data"], json_data["eligibility_date_str"]
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}: {e}")
        return None, None


def estimate_processing_date(data: dict[str, list[str]], eligibility_date_str: str = "1 March 2024"):
    df = pd.DataFrame(data)

    df["Recorded Date"] = pd.to_datetime(df["Recorded Date"], format="%B %Y")
    df["Current Processing Date"] = pd.to_datetime(df["Current Processing Date"], format="%d %b %Y")

    recorded_ordinal = df["Recorded Date"].map(datetime.toordinal)
    processing_ordinal = df["Current Processing Date"].map(datetime.toordinal)

    coefficients = np.polyfit(recorded_ordinal, processing_ordinal, 1)
    poly = np.poly1d(coefficients)

    eligibility_date = pd.to_datetime(eligibility_date_str)
    eligibility_ordinal = eligibility_date.toordinal()

    estimated_recorded_ordinal = (eligibility_ordinal - coefficients[1]) / coefficients[0]
    estimated_date = datetime.fromordinal(int(estimated_recorded_ordinal))

    plt.figure(figsize=(12, 8))
    
    # Plot the actual data points
    plt.scatter(df["Recorded Date"], df["Current Processing Date"], color='blue', s=50, label="Recorded Data Points")
    
    # Plot the trend line through actual data
    plt.plot(df["Recorded Date"], df["Current Processing Date"], color='blue', linestyle='dashed', alpha=0.7)

    # Create a reasonable projection range (extend 2 years beyond the last recorded date)
    last_recorded_date = df["Recorded Date"].max()
    projection_end = last_recorded_date + pd.DateOffset(years=2)
    
    # Create projection dates
    projection_dates = pd.date_range(start=df["Recorded Date"].min(), end=projection_end, freq='ME')
    projection_processing_dates = pd.to_datetime([datetime.fromordinal(int(poly(d.toordinal()))) for d in projection_dates])
    
    # Plot the projection line
    plt.plot(projection_dates, projection_processing_dates, color='red', linestyle='-', linewidth=2, label="Projection")

    # Add horizontal line for eligibility date
    plt.axhline(y=float(mdates.date2num(eligibility_date)), color='green', linestyle='--', linewidth=2, label=f"Eligibility Date ({eligibility_date.strftime('%d %b %Y')})")
    
    # Add vertical line for estimated date
    plt.axvline(x=float(mdates.date2num(estimated_date)), color='purple', linestyle='--', linewidth=2, label=f"Estimated Reached: {estimated_date.strftime('%B %Y')}")

    # Format the axes
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gca().yaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # Show every 3 months
    plt.gca().yaxis.set_major_locator(mdates.MonthLocator(interval=2))  # Show every 2 months
    
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels

    plt.xlabel("Recorded Date", fontsize=12)
    plt.ylabel("Current Processing Date", fontsize=12)
    plt.title("Processing Date Progression and Estimate", fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Set reasonable axis limits
    plt.xlim(df["Recorded Date"].min() - pd.DateOffset(months=1), projection_end)
    plt.ylim(df["Current Processing Date"].min() - pd.DateOffset(months=1), 
             max(eligibility_date, df["Current Processing Date"].max()) + pd.DateOffset(months=1))
    
    plt.tight_layout()
    plt.show()

    print(f"Estimated eligibility will be reached around: {estimated_date.strftime('%B %Y')}")
    print(f"Data spans from {df['Recorded Date'].min().strftime('%B %Y')} to {df['Recorded Date'].max().strftime('%B %Y')}")
    print(f"Processing dates span from {df['Current Processing Date'].min().strftime('%d %b %Y')} to {df['Current Processing Date'].max().strftime('%d %b %Y')}")


def main():
    """Main function to run the estimator."""
    data, eligibility_date_str = load_data_from_json()
    
    if data is None or eligibility_date_str is None:
        print("Failed to load data. Please check the JSON file.")
        return
    
    print(f"Loaded data with eligibility date: {eligibility_date_str}")
    estimate_processing_date(data, eligibility_date_str)


if __name__ == "__main__":
    main()
