import pandas as pd
import numpy as np
import argparse
import sys

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in miles between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    
    # Radius of earth in miles is approximately 3958.8
    r = 3958.8 
    return c * r

def main():
    # Set up argument parsing for the command line
    parser = argparse.ArgumentParser(description="Find TRI sites within a specified radius.")
    parser.add_argument('--lat', type=float, required=True, help="Receptor latitude (e.g., 30.4619808)")
    parser.add_argument('--lon', type=float, required=True, help="Receptor longitude (e.g., -91.1792221)")
    parser.add_argument('--radius', type=float, required=True, help="Radius in miles (e.g., 2.52)")
    parser.add_argument('--file', type=str, default='tri_voc_flexpart_2017.csv', help="Path to the CSV file")
    
    args = parser.parse_args()

    # Load the dataset
    try:
        df = pd.read_csv(args.file)
    except FileNotFoundError:
        print(f"Error: Could not find the file '{args.file}'. Please check the path.")
        sys.exit(1)

    # Ensure required coordinate columns exist
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        print("Error: The CSV file must contain 'latitude' and 'longitude' columns.")
        sys.exit(1)

    # Calculate distance for all rows
    df['distance_miles'] = haversine(df['longitude'], df['latitude'], args.lon, args.lat)

    # Filter sites that fall within the radius
    nearby_sites = df[df['distance_miles'] <= args.radius].copy()

    # Sort the results from closest to furthest
    nearby_sites.sort_values(by='distance_miles', inplace=True)

    # Output the results
    if nearby_sites.empty:
        print(f"\nNo sites found within {args.radius} miles of ({args.lat}, {args.lon}).")
    else:
        print(f"\nFound {len(nearby_sites)} site(s) within {args.radius} miles of ({args.lat}, {args.lon}):\n")
        
        # Select relevant columns to display (adjust these based on what you want to see)
        cols_to_show = ['facility_name', 'chemical', 'latitude', 'longitude', 'distance_miles']
        
        # Only display columns that actually exist in the dataframe
        display_cols = [col for col in cols_to_show if col in nearby_sites.columns]
        
        print(nearby_sites[display_cols].to_string(index=False))

if __name__ == '__main__':
    main()
