from ardu import Arduino


class Experiment:
    def __init__(self, vial_volume: float = 2.0, cleaning_station_volume: float = 5):
        self.cleaning_station_volume = cleaning_station_volume
        self.vial_volume = vial_volume
        self.arduino = Arduino()

    def get_temperature(self, cartridge_number: float):
        pass

    def set_temperature(self, temperature: float, cartridge_number: int):
        # Check that temperature is a positive number
        if temperature < 0:
            raise ValueError("Temperature should be a positive number")

        # Check that cartridge_number is a positive number
        if cartridge_number < 0:
            raise ValueError("Cartridge number should be a positive number")

        pass

    def clean_cell(self, vial_number: int, volume: float):
        pass

    def dispense_to_vial(self, vial_number: int, volume: float):
        # Check if the vial_number is between 0 and 1000
        if vial_number < 0 or vial_number > 1000:
            raise ValueError("Vial number should be between 0 and 1000")

        # Check if the volume is between 0 and 100
        if volume < 0 or volume > 100:
            raise ValueError("Volume should be between 0 and 100")

        pass

    def dispense_peristaltic(self, pump_number: int, volume: float):
        # Check if the pump_number is between 0 and 7
        if pump_number < 0 or pump_number > 7:
            raise ValueError("Pump number should be between 0 and 7")

        # Check if the volume is between 0 and 100
        if volume < 0 or volume > 100:
            raise ValueError("Volume should be between 0 and 100")

        pass
