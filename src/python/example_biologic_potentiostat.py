#%%
import time
import pandas as pd
from biologic import connect, BANDWIDTH
from biologic.techniques.cv import CVTechnique, CVParams, CVStep
from biologic.techniques.ocv import OCVTechnique, OCVParams
from biologic.techniques.peis import PEISTechnique, PEISParams
from biologic.techniques.cp import CPTechnique, CPParams, CPStep


########################################################################################
# Create a CV technique
print("CV technique")
Ei = CVStep(voltage = 0,
            scan_rate = 0.1,
            vs_initial = False)

E1 = CVStep(voltage = 1,
            scan_rate = 0.1,
            vs_initial = False)

E2 = CVStep(voltage = 0,
            scan_rate = 0.1,
            vs_initial = False)

Ef = CVStep(voltage = 0,
            scan_rate = 0.1,
            vs_initial = False)

params = CVParams(
    record_every_dE = 0.01,
    average_over_dE = False,
    n_cycles = 0,
    begin_measuring_i = 0.1,
    end_measuring_i = 0.5,
    Ei = Ei,
    E1 = E1,
    E2 = E2,
    Ef = Ef,
    bandwidth = BANDWIDTH.BW_5)



tech = CVTechnique(params)

# Push the technique to the Biologic
results = []
with connect('USB0', force_load = True) as bl:
    channel = bl.get_channel(2)
    runner = channel.run_techniques([tech])
    for result in runner:
        results.append(result.data)
    else:
        time.sleep(1)


# make results into a pandas dataframe
print("CV results")
df = pd.DataFrame(results)
print(df)
time.sleep(60)


########################################################################################
# Create a OCV technique
print("OCV technique")
params = OCVParams(
    rest_time_T=20, record_every_dE=0.01,
    record_every_dT=1, bandwidth=BANDWIDTH.BW_5,)

tech = OCVTechnique(params)

# Push the technique to the Biologic
results = []
with connect('USB0', force_load = True) as bl:
    channel = bl.get_channel(2)
    runner = channel.run_techniques([tech])
    for result in runner:
        results.append(result.data)
        # print(result.data)
    else:
        time.sleep(1)

# make results into a pandas dataframe
print("OCV results")
df = pd.DataFrame(results)
print(df)
time.sleep(60)


########################################################################################
# Create a EIS technique
print("EIS technique")
params = PEISParams(vs_initial=False,
                    initial_voltage_step=0.1,
                    duration_step=3,
                    record_every_dI=0.01,
                    record_every_dT=1,
                    correction=0,
                    final_frequency=1000,
                    initial_frequency=100000,
                    amplitude_voltage=0.01,
                    average_n_times=1,
                    frequency_number=10,
                    sweep=True,
                    wait_for_steady=False,
                    bandwidth=BANDWIDTH.BW_5)



tech = PEISTechnique(params)

# Push the technique to the Biologic
results = []
with connect('USB0', force_load = True) as bl:
    channel = bl.get_channel(2)
    runner = channel.run_techniques([tech])
    for result in runner:
        results.append(result.data)
        print(result.data)
    else:
        time.sleep(1)

# make results into a pandas dataframe
print("EIS results")
df = pd.DataFrame(results)
print(df)
time.sleep(60)

########################################################################################
# Create a CP technique
print("CP technique")
params = CPParams(record_every_dE=0.01,
                  record_every_dT=1,
                  n_cycles=1,
                  bandwidth=BANDWIDTH.BW_5,
                  )

tech = CPTechnique(params)

# Push the technique to the Biologic
results = []
with connect('USB0', force_load = True) as bl:
    channel = bl.get_channel(2)
    runner = channel.run_techniques([tech])
    for result in runner:
        results.append(result.data)
        print(result.data)
    else:
        time.sleep(1)

# make results into a pandas dataframe
print("CP results")
df = pd.DataFrame(results)
print(df)
# %%
