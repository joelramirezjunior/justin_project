import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy as sp
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import ttest_ind

# Parse command line arguments
parser = argparse.ArgumentParser(description="Analyze volleyball player dataset")
parser.add_argument("-p", "--plots", help="Save plots to figures folder", action="store_true")
parser.add_argument("-a", "--analysis", help="Conduct and display the analysis", action="store_true")
parser.add_argument("-g", "--gender", help="Specify the gender dataset to use (default: men)", choices=['men', 'women'], default='men')
args = parser.parse_args()

# Load the dataset based on the gender argument
data_path = f"./data/{args.gender}.csv"
data = pd.read_csv(data_path)

# Drop rows with missing values in continuous columns
subset_vars = ["Weight (kg)", "Height (cm)", "Spike (cm)", "Block (cm)", "Points", "Awards", "Matches", "Tournaments", "Position"]
data_clean = data.dropna(subset=subset_vars)

# Set visualization theme
sns.set_theme(style="darkgrid")
FIGURE_PATH = "./figures/" if args.plots else None

# Function to plot, calculate correlation, and save the figure
def plot_and_save(data, x_var, y_var, filename):
    plot = sns.jointplot(x=x_var, y=y_var, data=data, kind="reg", truncate=False, color="m")
    r, p = sp.stats.pearsonr(x=data[x_var], y=data[y_var])
    ax = plt.gca()
    plt.text(.05, .8, 'r={:.2f}'.format(r), transform=ax.transAxes)
    plt.text(.05, .9, 'p={:.2f}'.format(p), transform=ax.transAxes)
    if FIGURE_PATH:
        plt.savefig(FIGURE_PATH + filename)

# Function to conduct t-test analysis by position
def analyze_position(attribute):
    positions = data_clean["Position"].unique()
    for position in positions:
        group1 = data_clean[data_clean["Position"] == position][attribute]
        for position_comp in positions:
            if(position == position_comp): continue
            group2 = data_clean[data_clean["Position"] == position_comp][attribute]
            # Independent sample t-test
            t_stat, p_val = ttest_ind(group1, group2)
            if args.analysis:
                print(f"T-test for {position} vs {position_comp} - {attribute}:")
                print(f"T-statistic: {t_stat}, P-value: {p_val}")
                print("-"*50)
            # Plotting data
            if args.plots:
                plt.figure(figsize=(10, 6))
                sns.boxplot(x="Position", y=attribute, data=data_clean)
                plt.title(f"Box plot of {attribute} by Position")
                if FIGURE_PATH:
                    plt.savefig(FIGURE_PATH + f"{args.gender}_{attribute}_by_position.png")
        positions = positions[1:]

# Main functionality
if args.analysis or args.plots:
    plot_and_save(data_clean, "Spike (cm)", "Ranking", f"{args.gender}_Spike_vs_Ranking.png")
    plot_and_save(data_clean, "Height (cm)", "Spike (cm)", f"{args.gender}_Height_vs_Spike.png")
    plot_and_save(data_clean, "Height (cm)", "Block (cm)", f"{args.gender}_Height_vs_Block.png")
    plot_and_save(data_clean, "Weight (kg)", "Spike (cm)", f"{args.gender}_Weight_vs_Spike.png")
    plot_and_save(data_clean, "Height (cm)", "Awards", f"{args.gender}_Height_vs_Awards.png")
    
    if args.analysis:
        continuous_vars = subset_vars
        correlations = data_clean[["Ranking"] + continuous_vars].corr(method='pearson')
        ranking_correlations = correlations["Ranking"].drop("Ranking")
        
        # Calculating R^2 values by squaring the Pearson correlation values
        r2_values = ranking_correlations**2
        
        print("Pearson Correlation Coefficients with 'Ranking':\n")
        print(ranking_correlations)
        print("\nCoefficient of Determination (R^2) with 'Ranking':\n")
        print(r2_values)
        print("\n" + "-"*50 + "\n")


    analyze_position("Height (cm)")
    analyze_position("Weight (kg)")
