## ## Load packages
## import pandas as pd
## import statsmodels.api as sm
## import statsmodels.formula.api as smf
## import matplotlib.pyplot as plt
## import seaborn as sns
## from statsmodels.stats.multicomp import pairwise_tukeyhsd

## ## Load the data
## d_trees = pd.read_csv("../../Datasets/TreesChamagne2017_Lab_modified.csv",
##                       sep = ';', decimal = ',')

## # Rename variables because "." causes problems in python
## d_trees.rename(columns = {'growth.rate': 'growth_rate'}, inplace = True)
## d_trees.rename(columns = {'Density.tree.Class': 'Density_tree_Class'}, inplace = True)

## ## Inspect the data
## print(d_trees.info())
## print(d_trees.head())

## ## Clean figure object
## plt.clf()
## 
## ## Boxplot for growth rate by species
## sns.boxplot(x = 'species', y = 'growth_rate', data = d_trees)

## ## The following line of code is necessary when running line by line.
## ## When compiling the PDF, it is not necessary
## plt.show()

## ## Fit a linear model: growth.rate ~ species
## lm_trees_1 = smf.ols('growth_rate ~ species', data = d_trees).fit()
## print(lm_trees_1.params)

## ## Summary
## print(lm_trees_1.summary())

## ## Fit a null model: growth.rate ~ 1
## lm_trees_0 = smf.ols('growth_rate ~ 1', data = d_trees).fit()
## print(lm_trees_0.params)

## ## Summary
## print(lm_trees_0.summary())

## ## Compare the two models
## anova_comparison = sm.stats.anova_lm(lm_trees_0, lm_trees_1)
## print(anova_comparison)

## ## Check whether Oak and Spruce differ in terms of growth rates
## # Filter dataset to include only Oak and Spruce
## d_trees_filtered = d_trees[d_trees['species'].isin(['Oak', 'Spruce'])]
## tukey_results = pairwise_tukeyhsd(endog = d_trees_filtered['growth_rate'].astype(float),
##                                   groups = d_trees_filtered['species'])
## 
## # Print summary
## print(tukey_results)

## ## Add Density.tree.Class and SiteID to the model
## lm_trees_2 = smf.ols('growth_rate ~ species + Density_tree_Class + SiteID',
##                      data = d_trees).fit()
## print(lm_trees_2.summary())
## ##
## ## Check
## print(lm_trees_2.model.formula)

## ## Test the two newly added variables
## anova_added_var = sm.stats.anova_lm(lm_trees_2, typ = 2)
## anova_added_var_df = pd.DataFrame(anova_added_var)
## print(anova_added_var_df)

## ## SiteID wasn't correctly coded. We recode it.
## 
## ## Add a factor version of SiteID
## d_trees['SiteID_fac'] = d_trees['SiteID'].astype('category')

## ## Update model to use SiteID.fac instead of SiteID
## lm_trees_3 = smf.ols('growth_rate ~ species + Density_tree_Class + SiteID_fac',
##                      data = d_trees).fit()
## # print(lm_trees_3.summary())

## ## Test the variables
## anova_added_var2 = sm.stats.anova_lm(lm_trees_3, typ = 2)
## anova_added_var2_df = pd.DataFrame(anova_added_var2)
## print(anova_added_var2_df)

## ## Add age to the model
## lm_trees_4 = smf.ols('growth_rate ~ species + Density_tree_Class + SiteID_fac + age',
##                      data = d_trees).fit()
## # print(lm_trees_4.summary())

## ## Global F-test
## anova_global = sm.stats.anova_lm(lm_trees_4)
## print(anova_global)

## ## Check coefficient for age
## # Get summary output as text
## lm_trees_4_summary_text = lm_trees_4.summary().as_text()
## 
## # Convert to list of lines
## summary_lines = lm_trees_4_summary_text.split("\n")
## 
## # Extract specific lines (equivalent to R's c(10,11,62))
## selected_lines = [summary_lines[i] for i in [12, 13, 64]]
## 
## # Print the selected lines
## for line in selected_lines:
##     print(line)

## ## Compare two models
## anova_comparison2 = sm.stats.anova_lm(lm_trees_0, lm_trees_4)
## print(anova_comparison2)

## ## Sequential sum of squares
## lm_trees_4.model.formula
## print(sm.stats.anova_lm(lm_trees_4))
## ##
## ## Let's move *species* at the end
## lm_trees_4_again = smf.ols('growth_rate ~ Density_tree_Class + SiteID_fac + age + species',
##                      data = d_trees).fit()
## print(sm.stats.anova_lm(lm_trees_4_again))

## # Tukey HSD test for species (i.e., testing all pairwise comparisons)
## tukey_species = pairwise_tukeyhsd(endog = d_trees['growth_rate'].astype(float),
##                                   groups = d_trees['species'],
##                                   alpha = 0.05)
## print(tukey_species)
## ## Unfortunately, the plot doesn't seem to be as straightforward as in R

## # Add interaction between age and species
## lm_trees_5 = smf.ols('growth_rate ~ species + Density_tree_Class + SiteID_fac + age + age:species',
##                      data = d_trees).fit()
## # print(lm_trees_5.summary())
## print(sm.stats.anova_lm(lm_trees_5))

## plt.clf()
## ## Visualise age effect over all data
## g = sns.lmplot(x = 'age', y = 'growth_rate', data = d_trees,
##                height = 4, aspect = 1, ci = 95)

## plt.show()

## plt.clf()
## ## Visualise age effect for each species
## g = sns.lmplot(x = 'age', y = 'growth_rate', data = d_trees, col = 'species',
##                height = 4, aspect = 1, ci = 95)

## plt.show()

## print(lm_trees_1.summary())
## print(sm.stats.anova_lm(lm_trees_1))

## ## Relevel *species*
## d_trees['species_relevelled'] = pd.Categorical(d_trees['species'],
##                                                categories = ['Oak', 'Beech', 'Spruce', 'Larch'],
##                                                ordered = True)
## 
## lm_trees_1_relevelled = smf.ols('growth_rate ~ species_relevelled', data = d_trees).fit()
## print(lm_trees_1_relevelled.summary())

## print(sm.stats.anova_lm(lm_trees_1_relevelled))
