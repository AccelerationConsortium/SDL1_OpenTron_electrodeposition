# Import for plotting EIS data
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import os
from matplotlib import colormaps

list(colormaps)

sample_area = 0.2827


def rename_columns(df: pd.DataFrame):
    # Loop through column headers and rename them
    for i in range(len(df.columns)):
        # If a column doesn't have a name, name it "Unnamed"
        if df.columns[i] == "" or df.columns[i] == "Unnamed: 0":
            df.columns.values[i] = "Point"

        # If a column is named "Ewe" or "Working electrode DC Voltage [V]" rename it to "Working electrode DC Voltage [V]"
        if (
            df.columns[i] == "Ewe"
            or df.columns[i] == "Working electrode DC Voltage [V]"
            or df.columns[i] == "Working Electrode Voltage [V]"
            or df.columns[i] == "Ewe_avg"
        ):
            df.columns.values[i] = "Working electrode vs. reference potential [V]"

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


# Plot Nyquist plot
def plot_eis_nyquist(df, x_col, y_col, title, x_label, y_label, file_name=None):
    # Remove rows with NaN values in either x_col or y_col
    df = df.dropna(subset=[x_col, y_col])

    # Make column x_col and y_col absolute
    df.loc[:, x_col] = abs(df[x_col])
    df.loc[:, y_col] = abs(df[y_col])

    plt.figure()
    plt.plot(df[x_col], df[y_col], "o-")
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # Make an array with the first 15 values of y_col
    y_values = df[y_col].head(11)
    # Find the minimum value of the absolute value of y_col
    min_y = min(y_values)

    # Find the corresponding index
    min_y_index = df[y_col].idxmin()

    # Find the corresponding x value
    min_x = df[x_col][min_y_index]
    print(f"Ohmic resistance: {round(min_x, 3)} Ohm")

    # Plot the minimum value
    plt.plot(min_x, min_y, "ro")

    if file_name:
        plt.savefig("data/" + file_name + ".jpg")
    else:
        plt.show()

    plt.close()


def plot_cv(
    df, x_col, y_col, title, x_label, y_label, cycle_label=None, file_name=None
):
    # Remove rows with NaN values in either x_col or y_col
    try:
        df = df.dropna(subset=[x_col, y_col])

        plt.figure()
        if cycle_label is not None:
            plt.scatter(df[x_col], df[y_col], c=df[cycle_label], cmap="viridis")
            plt.colorbar(label="Cycle")
        else:
            plt.plot(df[x_col], df[y_col], "o-")
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        if file_name:
            plt.savefig("data/" + file_name + ".jpg")
        else:
            plt.show()

        plt.close()
    except Exception as e:
        print(f"No KeyError, when it should not be, error: {e}")


def plot_log_cv(
    df, x_col, y_col, title, x_label, y_label, cycle_label=None, file_name=None
):
    # Remove rows with NaN values in either x_col or y_col
    try:
        df = df.dropna(subset=[x_col, y_col])

        fig, axs = plt.subplots(
            1, 2, figsize=(12, 5)
        )  # Create a figure with two subplots

        # Plot original data
        if cycle_label is not None:
            im = axs[0].scatter(df[x_col], df[y_col], c=df[cycle_label], cmap="viridis")
            axs[0].colorbar(im, label="Cycle")
        else:
            axs[0].plot(df[x_col], df[y_col], "o-")
        axs[0].set_title(title)
        axs[0].set_xlabel(x_label)
        axs[0].set_ylabel(y_label)

        # Plot x_col vs log_current
        if cycle_label is not None:
            axs[1].set_yscale("log")
            im2 = axs[1].scatter(
                df[x_col],
                np.abs(df[y_col]),
                c=df[cycle_label],
                cmap="viridis",
            )
            axs[1].colorbar(im2, label="Cycle")
        else:

            axs[1].plot(df[x_col], np.abs(df[y_col]), "o-")
        axs[1].set_title(f"Cathodic CV scan\nLogarithmic scale\n{file_name}")
        axs[1].set_xlabel(x_label)
        axs[1].set_ylabel("log(current) [A/cm2]")
        axs[1].set_yscale("log")
        axs[1].grid()
        # axs[1].yaxis.set_view_interval(0, np.log(-1), ignore=False)
        plt.tight_layout()  # Adjust subplots to fit into the figure area

        if file_name:
            plt.savefig("data/" + file_name + ".jpg")
        else:
            plt.show()

        plt.close()
    except KeyError:
        print("There should be no KeyError, but there is...")

# Loop through all .csv files in the folder and plot the Nyquist plot for each file containing "EIS" in the filename. Save plot under the same filename with .jpg extension.
for file in os.listdir(path="data/"):
    # If both "EIS" and ".csv" are in the filename, read the file and plot the Nyquist plot
    if ".csv" in file:
        file_name = file.split(".")[0]
        print(f"Reading {file}")

        if "EIS" in file:
            data = pd.read_csv(
                "data/" + file,
                sep=",",
                header=0,
                encoding="utf8",
            )

            data = rename_columns(data)

            # If there are columns named "Real Impedance" and "Imaginary Impedance" where the value is = 0.0, drop the rows
            data = data[
                (data["Real Impedance"] != 0.0) & (data["Imaginary Impedance"] != 0.0)
            ]

            # Take the filename and make it the same but with .jpg extension

            plot_eis_nyquist(
                data,
                "Real Impedance",
                "Imaginary Impedance",
                "Nyquist plot",
                "Real Impedance [Ohm]",
                "Imaginary Impedance [Ohm]",
                file_name,
            )

        if "CV" in file:
            data = pd.read_csv(
                "data/" + file,
                sep=",",
                header=0,
                encoding="utf8",
            )
            if "Ref CV" in file:  # Biologic data
                surface_pt_wire = 0.0475
                data["I_avg"] = data["I_avg"] / surface_pt_wire

                plot_cv(
                    df=data,
                    x_col="Ewe_avg",
                    y_col="I_avg",
                    title="Cyclic Voltammetry\nNot ohmic corrected",
                    x_label="Working electrode vs. reference potential [V]",
                    y_label="Current [A/cm2]",
                    cycle_label="cycle",
                    file_name=file_name,
                )
            else:  # Admiral data
                df = rename_columns(data)

                # Make a column "cycle" and make it so that it starts with 0 and increases by 1 every time the is a local minima in "Working electrode vs. reference potential [V]"
                df["cycle"] = (
                    df["Working electrode vs. reference potential [V]"]
                    < df["Working electrode vs. reference potential [V]"].shift()
                ).cumsum()

                # Divide column "Current [A]" by sample_surface_area to get it in A/cm^2
                df["Current [A]"] = df["Current [A]"] / sample_area

                plot_cv(
                    df=df,
                    x_col="Working electrode vs. reference potential [V]",
                    y_col="Current [A]",
                    title="Cyclic Voltammetry\nNot ohmic corrected",
                    x_label="Working electrode vs. reference potential [V]",
                    y_label="Current [A/cm2]",
                    file_name=file_name,
                )

        if "Cathodic scan" in file:
            data = pd.read_csv(
                "data/" + file,
                sep=",",
                header=0,
                encoding="utf8",
            )
            df = rename_columns(data)

            # Make a column "cycle" and make it so that it starts with 0 and increases by 1 every time the is a local minima in "Working electrode vs. reference potential [V]"
            df["cycle"] = (
                df["Working electrode vs. reference potential [V]"]
                < df["Working electrode vs. reference potential [V]"].shift()
            ).cumsum()

            # Divide column "Current [A]" by sample_surface_area to get it in A/cm^2
            df["Current [A]"] = df["Current [A]"] / sample_area

            plot_log_cv(
                df=df,
                x_col="Working electrode vs. reference potential [V]",
                y_col="Current [A]",
                title="Cyclic Voltammetry\nNot ohmic corrected",
                x_label="Working electrode vs. reference potential [V]",
                y_label="Current [A/cm2]",
                file_name=file_name,
            )

        if "Electrodeposition" in file or "CP" in file:
            data = pd.read_csv(
                "data/" + file,
                sep=",",
                header=0,
                encoding="utf8",
            )
            data = rename_columns(data)

            plot_cv(
                df=data,
                x_col="Time [s]",
                y_col="Working electrode vs. reference potential [V]",
                title="Chrono Potentiommetry\nNot ohmic corrected",
                x_label="Time [s]",
                y_label="Working electrode vs. reference potential [V]",
                file_name=file_name,
            )
