list_of_pump_relays = ([0, 1, 2, 3, 4, 5],)  # Pumps connected to which relays
list_of_ultrasonic_relays = ([6, 7],)  # Ultrasonic connected to which relays
pump_slope = ({0: 2.0369, 1: 2.0263, 2: 2.0263, 3: 2.0263, 4: 2.0263, 5: 2.0263},)
pump_intercept = {0: 0.1407, 1: 0.0607, 2: 0.0607, 3: 0.0607, 4: 0.0607, 5: 0.0607}
OHMIC_CORRECTION_FACTOR = 0.9
sample_surface_area = 0.2827
current_density = 0.020  # A/cm^2
current_at_sample = sample_surface_area * current_density
volume_of_well = 3.9  # mL
volume_of_pipette = 1  # mL

# Content of each peristaltic pump vs. relay number
peristaltic_pump_content = {
    "Flush_tool_Drain": 0,
    "Flush_tool_H2O": 1,
    "Flush_tool_HCl": 2,
    "Cartridge_Drain": 3,
    "Cartidge_H2O": 4,
    "Cartridge_HCl": 5,
}

labware_paths = {
    "nistall_4_tiprack_1ul": "src/opentron_labware/nistall_4_tiprack_1ul.json",
    "nis_15_wellplate_3895ul": "src/opentron_labware/nis_15_wellplate_3895ul.json",
    "nis_2_wellplate_30000ul": "src/opentron_labware/nis_2_wellplate_30000ul.json",
    "nis_8_reservoir_25000ul": "src/opentron_labware/nis_8_reservoir_25000ul.json",
}

labware_tools = {
    "Ni_electrode": "A1",
    "Flush_tool": "B1",
    "Ag_electrode": "A2",
    "OER_electrode": "B2",
}
tool_x_offset = {
    "Ni_electrode": 0.75,
    "Flush_tool": 0.5,
    "Ag_electrode": 1,
    "OER_electrode": 0.75,
}
tool_y_offset = {
    "Ni_electrode": 0.75,
    "Flush_tool": 0.5,
    "Ag_electrode": 0,
    "OER_electrode": 0,
}
tool_z_offset = {
    "Ni_electrode": 5,
    "Flush_tool": 10,
    "Ag_electrode": 2,
    "OER_electrode": 5,
}
tool_z_dropoff = {
    "Ni_electrode": 11,
    "Flush_tool": 11,
    "Ag_electrode": 8,
    "OER_electrode": 11,
}
wells = {
    0: "A1",
    1: "A2",
    2: "A3",
    3: "A4",
    4: "A5",
    5: "B1",
    6: "B2",
    7: "B3",
    8: "B4",
    9: "B5",
    10: "C1",
    11: "C2",
    12: "C3",
    13: "C4",
}

pipetteable_chemicals = {
    "NH4OH": "A4",
    "KCHO": "B4",
    "KOH": "B4",
    "Ni": "A1",
    "Fe": "A2",
    "Cr": "A3",
    "Mn": "A4",
    "Co": "B1",
    "Zn": "B2",
    "Cu": "B3",
}
pipetteable_chemical_racks = {
    "NH4OH": "nis_8_reservoir_25000ul_7",
    "KCHO": "nis_8_reservoir_25000ul_7",
    "KOH": "nis_8_reservoir_25000ul_11",
    "Ni": "nis_8_reservoir_25000ul_11",
    "Fe": "nis_8_reservoir_25000ul_11",
    "Cr": "nis_8_reservoir_25000ul_11",
    "Mn": "nis_8_reservoir_25000ul_11",
    "Co": "nis_8_reservoir_25000ul_11",
    "Zn": "nis_8_reservoir_25000ul_11",
    "Cu": "nis_8_reservoir_25000ul_11",
}


pipette_tips = {
    "NH4OH": "H1",
    "KCHO": "H2",
    "KOH": "H3",
    "Ni": "H4",
    "Fe": "H5",
    "Cr": "H6",
    "Mn": "H7",
    "Co": "H9",
    "Zn": "H10",
    "Cu": "H11",
}

pump_slope = {0: 2.05, 1: 2.13, 2: 1.93, 3: 2.24, 4: 1.86, 5: 1.85}
pump_intercept = {0: 0.082, 1: 0.058, 2: 0.0686, 3: 0.0362, 4: 0.0356, 5: 0.0186}
