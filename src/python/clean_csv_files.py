import pandas as pd


def rename_columns(df: pd.DataFrame):
    # Loop through column headers and rename them
    for i in range(len(df.columns)):
        # If a column doesn't have a name, name it "Unnamed"
        if df.columns[i] == "" or df.columns[i] == "Unnamed: 0":
            df.columns.values[i] = "Point"

        # If a column is named "Ewe" or "Working electrode DC Voltage [V]" rename it to "Working electrode DC Voltage [V]"
        if df.columns[i] == "Ewe_avg":
            df.columns.values[i] = "Working"

        # If a column is named "Ece" or "Ec" rename it to " Counter electrode vs. reference electrode potential [V]"
        elif (
            df.columns[i] == "Ece"
            or df.columns[i] == "Ec"
            or df.columns[i] == "Ece_avg"
        ):
            df.columns.values[i] = (
                "Counter electrode vs. reference electrode potential [V]"
            )

        # If a column is named "I_avg" or "I" rename it to "Current [A]" and divide the column by 1000
        elif df.columns[i] == "I_avg" or df.columns[i] == "I":
            df[df.columns[i]] = df[df.columns[i]] / 1000
            df.columns.values[i] = "Current [A]"

        # If the column is named "Working Electrode Current [A]" or "DC Current [A]" rename it to "Current [A]"
        elif (
            df.columns[i] == "Working Electrode Current [A]"
            or df.columns[i] == "DC Current [A]"
        ):
            df.columns.values[i] = "Current [A]"

        # If the column is named "freq" rename it to "Frequency [Hz]"
        elif df.columns[i] == "freq":
            df.columns.values[i] = "Frequency [Hz]"

        # If the column is named "I_mod" make a new column named "Real Impedance" = "Ewe_mod"/"I_mod"*cos("phase_Zwe")
        elif df.columns[i] == "I_mod":
            df["Real Impedance"] = (
                df["Ewe_mod"]
                / df["I_mod"]
                * df["phase_Zwe"].apply(lambda x: math.cos(x * (math.pi / 180)))
            )

            df["Imaginary Impedance"] = (df["Ewe_mod"] / df["I_mod"]).mul(
                df["phase_Zwe"].apply(lambda x: math.sin(x * (math.pi / 180)))
            )

        # If the column is named "Timestamp" or "time" rename it to "Time [s]"
        elif df.columns[i] == "Timestamp" or df.columns[i] == "time":
            df.columns.values[i] = "Time [s]"

    return df


# Open a csv file and load it into a pandas dataframe
dataframe = pd.read_csv("95 Ref CV after.csv")


print(dataframe["Ewe_avg"])

# Rename the columns of the dataframe
dataframe = rename_columns(dataframe)

print(dataframe["Working"])
