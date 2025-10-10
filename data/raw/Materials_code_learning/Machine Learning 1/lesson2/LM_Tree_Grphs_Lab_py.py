## Load packages
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns

# Getting data

# Load the data
d_trees = pd.read_csv("../../Datasets/TreesChamagne2017_Lab_modified.csv",
                      sep = ';', decimal = ',')

# rename variables because "." causes problems in R
d_trees.rename(columns = {'growth.rate': 'growth_rate'}, inplace = True)
d_trees.rename(columns = {'diversity.site': 'diversity_site'}, inplace = True)
d_trees.rename(columns = {'density.site': 'density_site'}, inplace = True)

# Inspect the data
print(d_trees.info())
print(d_trees.head())

plt.clf()
# ----graphDiversitySite----
sns.scatterplot(x = 'diversity_site', y = 'growth_rate', data = d_trees)

## This is needed only if you run line by line.
## If you compile the document to a PDF, it is not needed.
plt.show()

plt.clf()
# ----graphDiversitySiteWithRegrLine----
sns.lmplot(x = 'diversity_site', y = 'growth_rate', data = d_trees, ci = 95)

plt.show()

plt.clf()
# ----graphDiversitySiteWithSmoother----
sns.regplot(x = 'diversity_site', y = 'growth_rate', data = d_trees,
           lowess = True)
## CI are not supported when lowess = True

plt.show()

plt.clf()
# ----graphDensity----
sns.lmplot(x = 'density_site', y = 'growth_rate', data = d_trees, lowess = True)

plt.show()

plt.clf()
# ----graphAge----
sns.lmplot(x = 'age', y = 'growth_rate', data = d_trees, lowess = True)

plt.show()

# ----GraphSpecies----
sns.boxplot(x = 'species', y = 'growth_rate', data = d_trees)

plt.show()

plt.clf()
# ----graphDiversityGrouped----
sns.lmplot(x = 'diversity_site', y = 'growth_rate', hue = 'species',
    data = d_trees, lowess = True, scatter_kws = {'alpha': 0.7}
)

plt.show()

plt.clf()
# ----graphDiversityPanelling----
g = sns.FacetGrid(d_trees, col = 'species')
g.map_dataframe(sns.scatterplot, x = 'diversity_site', y = 'growth_rate')
g.map_dataframe(sns.regplot, x = 'diversity_site', y = 'growth_rate', 
                scatter = False, ci = None, lowess = True)

plt.show()

plt.clf()
# ----graphDiversityPanellingRegressionLines----
g = sns.FacetGrid(d_trees, col = 'species')
g.map_dataframe(sns.scatterplot, x = 'diversity_site', y = 'growth_rate')
g.map_dataframe(sns.regplot, x = 'diversity_site', y = 'growth_rate', 
                scatter = False, ci = 95)

plt.show()

plt.clf()
# ----lm0----
lm_trees_0 = smf.ols(
    'growth_rate ~ species + age + density_site + diversity_site + species:age + species:density_site + species:diversity_site',
    data = d_trees
).fit()
print(lm_trees_0.summary())

anova = sm.stats.anova_lm(lm_trees_0)
print(anova)

# ----drop1InteractionLm0----
lm_trees_1 = smf.ols(
    'growth_rate ~ species + age + density_site + diversity_site + species:age + species:density_site',
    data = d_trees
).fit()
print(lm_trees_1.summary())

anova_1 = sm.stats.anova_lm(lm_trees_1)
print(anova_1)
