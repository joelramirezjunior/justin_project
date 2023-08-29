import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp

# Load the dataset
data = pd.read_csv("men.csv")

# Drop rows with missing values in continuous columns
data_clean = data.dropna(subset=["Weight (kg)", "Height (cm)", "Spike (cm)", "Block (cm)", "Points", "Awards", "Matches", "Tournaments"])

# List of continuous variables
continuous_vars = ["Weight (kg)", "Height (cm)", "Spike (cm)", "Block (cm)", "Points", "Awards", "Matches", "Tournaments"]



spike = data_clean[["Spike (cm)"]]
ranking = data_clean[["Ranking"]]



sns.set_theme(style="darkgrid")

s_r = sns.jointplot(x="Spike (cm)", y="Ranking", data=data_clean,
                  kind="reg", truncate=False,
                  color="m",)

ax = plt.gca()
r, p = sp.stats.pearsonr(x=data_clean['Spike (cm)'], y=data_clean['Ranking'])
# annotate the pearson correlation coefficient text to 2 decimal places
plt.text(.05, .8, 'r={:.2f}'.format(r), transform=ax.transAxes)
plt.text(.05, .9, 'p={:.2f}'.format(p), transform=ax.transAxes)


plt.savefig("Spike vs Ranking")

h_s = sns.jointplot(x="Height (cm)", y="Spike (cm)", data=data_clean,
                  kind="reg", truncate=False,
                  color="m",)

r, p = sp.stats.pearsonr(x=data_clean["Height (cm)"], y=data_clean["Spike (cm)"])
# annotate the pearson correlation coefficient text to 2 decimal places
ax = plt.gca()
plt.text(.05, .8, 'r={:.2f}'.format(r), transform=ax.transAxes)
plt.text(.05, .9, 'p={:.10f}'.format(p), transform=ax.transAxes)
plt.savefig("Height vs Spike")


h_b = sns.jointplot(x="Height (cm)", y="Block (cm)", data=data_clean,
                  kind="reg", truncate=False,
                  color="m",)

plt.savefig("Height vs Block")

w_s = sns.jointplot(x ="Weight (kg)", y= "Spike (cm)", data = data_clean, 
                    kind="reg", truncate=False, color="m",)


plt.savefig("Weight vs Spike")


h_a = sns.jointplot(x="Height (cm)", y="Awards", data=data_clean,
                  kind="reg", truncate=False,
                  color="m",)

r, p = sp.stats.pearsonr(x=data_clean["Height (cm)"], y=data_clean["Awards"])
# annotate the pearson correlation coefficient text to 2 decimal places
ax = plt.gca()
plt.text(.05, .8, 'r={:.2f}'.format(r), transform=ax.transAxes)
plt.text(.05, .9, 'p={:.10f}'.format(p), transform=ax.transAxes)
plt.savefig("height vs awards")



position_and_height  = sns.catplot(x="Position", y="Awards", data=data_clean)

plt.show()
# Calculate Pearson correlation coefficients for each continuous variable with respect to 'Ranking'
correlations = data_clean[["Ranking"] + continuous_vars].corr(method='pearson')
ranking_correlations = correlations["Ranking"].drop("Ranking")


print("Pearson Correlation Coefficients with 'Ranking':\n")
print(ranking_correlations)
print("\n" + "-"*50 + "\n")




# # ANOVA for categorical variables
# categorical_vars = ["Name", "Nationality", "Position", "Birthdate", "Dominant hand", "Added by"]
# anova_results = {}

# for var in categorical_vars:
#     model = ols(f'Ranking ~ C({var})', data=data_clean).fit()
#     anova_table = sm.stats.anova_lm(model, typ=2)
#     anova_results[var] = anova_table

# for var, result in anova_results.items():
#     print(f"ANOVA results for {var}:\n")
#     print(result)
#     print("\n" + "-"*50 + "\n")
