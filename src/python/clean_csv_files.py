import pandas as pd

# Open a csv file and load it into a pandas dataframe
dataframe = pd.read_csv("95 Ref CV after.csv")

# Find the cells with the scientific notation (eg. -1.000000e-05) and convert it into a normal float number
dataframe = dataframe.applymap(lambda x: "%.10f" % x if isinstance(x, float) else x)

# Save the dataframe back to a csv file
dataframe.to_csv("95 Ref CV after data_cleaned.csv", index=False)
