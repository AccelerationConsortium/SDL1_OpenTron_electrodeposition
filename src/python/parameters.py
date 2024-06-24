list_of_pump_relays = ([0, 1, 2, 3, 4, 5],)  # Pumps connected to which relays
list_of_ultrasonic_relays = ([6, 7],)  # Ultrasonic connected to which relays
pump_slope = ({0: 2.0369, 1: 2.0263, 2: 2.0263, 3: 2.0263, 4: 2.0263, 5: 2.0263},)
pump_intercept = {0: 0.1407, 1: 0.0607, 2: 0.0607, 3: 0.0607, 4: 0.0607, 5: 0.0607}

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
    "nis_4_tip_rack_1ul": "../opentron_labware/nis_4_tip_rack_1ul.json",
    "nis_15_wellplate_3895ul":"../opentron_labware/nis_15_wellplate_3895ul.json"
    "nis_2_wellplate_30000ul": "../opentron_labware/nis_2_wellplate_30000ul.json",
    "nis_8_reservoir_25000ul": "../opentron_labware/nis_8_reservoir_25000ul.json",
}

labware_tools = {
    "Ni_electrode": "A1",
    "Flush_tool": "A2",
    "Ag_electrode": "B1",
    "OER_electrode": "B2",
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
    "NH4OH": "A1",
    "KCHO": "A2",
    "KOH": "A3",
    "Ni": "A4",
    "Fe": "B1",
    "Cr": "B2",
    "Mn": "B3",
    "Co": "B4",
    "Zn": "A1",
    "Cu": "A2",
}


pipette_tips = {
    "NH4OH": "A1",
    "KCHO": "A2",
    "KOH": "A3",
    "Ni": "A4",
    "Fe": "A5",
    "Cr": "A6",
    "Mn": "A7",
    "Co": "A9",
    "Zn": "A10",
    "Cu": "A11",
}
