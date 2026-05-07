import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

def main():
    # (1) Setup command line arguments
    parser = argparse.ArgumentParser(description='Plot receptor concentrations.')
    parser.add_argument('--site-code', type=str, required=True, 
                        help='The site code used to identify the CSV file.')
    parser.add_argument('--ground-truth-mean', type=float, required=True, 
                        help='The known ground truth mean concentration.')
    
    args = parser.parse_args()
    site_code = args.site_code
    gt_mean = args.ground_truth_mean

    # Construct the filename based on the site code
    file_name = f'receptor_conc_2017_{site_code}.csv'
    
    if not os.path.exists(file_name):
        print(f"Error: File {file_name} not found.")
        return

    # Load the dataset
    df = pd.read_csv(file_name)

    # (2) Calculate the annual simulated mean
    # Sum of all values divided by the number of rows
    sim_mean = df['concentration_ng_m3'].sum() / len(df)

    # Process data for the bar plot (Mean per day)
    df['simulation_date'] = df['simulation_date'].astype(str)
    df_grouped = df.groupby('simulation_date')['concentration_ng_m3'].mean().reset_index()
    df_grouped = df_grouped.sort_values('simulation_date')

    # (3) Create the Plot
    plt.figure(figsize=(12, 7))
    
    # Plot bars for daily concentration
    plt.bar(df_grouped['simulation_date'], df_grouped['concentration_ng_m3'], 
            color='skyblue', alpha=0.7, label='Daily Mean Concentration')

    # Add the annual simulated mean and ground truth mean lines
    plt.axhline(y=sim_mean, color='red', linestyle='--', linewidth=2, 
                label=f'Annual Sim Mean: {sim_mean:.4f} $ng/m^3$')
    plt.axhline(y=gt_mean, color='green', linestyle='-', linewidth=2, 
                label=f'Ground Truth Mean: {gt_mean:.4f} $ng/m^3$')

    # Formatting the plot
    plt.xlabel('Simulation Date', fontsize=12)
    plt.ylabel('Concentration ($ng/m^3$)')
    plt.title(f'Receptor Concentration at {site_code}')
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.grid(axis='y', linestyle=':', alpha=0.6)
    
    # Save the output
    output_plot = f'concentration_plot_{site_code}.png'
    plt.tight_layout()
    plt.savefig(output_plot)
    
    print(f"Analysis Complete for Site: {site_code}")
    print(f"Annual Simulated Mean: {sim_mean:.6f}")
    print(f"Ground Truth Mean: {gt_mean:.6f}")
    print(f"Plot saved as {output_plot}")

if __name__ == "__main__":
    main()
