import pandas as pd
import matplotlib.pyplot as plt
file_iris=pd.read_csv("w9/iris.csv")
# Basic line plot of sepal length
plt.plot(file_iris['sepal_length'])
plt.title("Line Plot of Sepal Length")
plt.xlabel("Index")
plt.ylabel("Sepal Length")
plt.show()

# Box plot for Sepal Length
plt.boxplot(file_iris['sepal_length'])
plt.title("Box Plot of Sepal Length")
plt.ylabel("Sepal Length")
plt.show()

# Histogram for petal length
plt.hist(file_iris['petal_length'], bins=20, color='skyblue', edgecolor='black')
plt.title("Histogram of Petal Length")
plt.xlabel("Petal Length (cm)")
plt.ylabel("Frequency")
plt.grid(True)
plt.show()

# Scatter plot for length and width
plt.scatter(file_iris['petal_length'], file_iris['petal_width'], color='green')
plt.title("Petal Length vs Petal Width")
plt.xlabel("Petal Length (cm)")
plt.ylabel("Petal Width (cm)")
plt.grid(True)
plt.show()

# Group by species and calculate the mean of each feature
means = file_iris.groupby('species').mean()
print(means)
# Plot petal length for each species, line plots
plt.plot(means.index, means['petal_length'], marker='o', linestyle='-', label='Petal Length')
plt.plot(means.index, means['petal_width'], marker='s', linestyle='--', label='Petal Width')
plt.title("Mean Petal Size by Species")
plt.xlabel("Species")
plt.ylabel("cm")
plt.legend()
plt.grid(True)
plt.show()


