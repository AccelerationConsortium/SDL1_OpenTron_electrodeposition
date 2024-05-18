import logging
from dataclasses import dataclass

LOGGER = logging.getLogger(__name__)


class Singleton(type):
    """Metaclass for singleton pattern."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass
class SerialConnection:
    """Initialize configuration for serial connection."""

    serial_port_pump: str  # "/dev/ttyACM0"
    serial_port_pid: str  # "/dev/ttyACM0"
    serial_port_probe: str
    baud_rate: int = 9600
    timeout: float = 0.1


@dataclass
class Robot:
    """Initialize configuration for robot."""

    serial_connection: SerialConnection
    pump_count: int
    load_time: float = 5  # wait time in seconds


class Config(metaclass=Singleton):
    """Initialize all configurations and check whether the config file exist.

    Args:
        metaclass (_type_, optional): _description_. Defaults to Singleton.
    """

    # check all initial settings here
    def __init__(self):
    try:
        
        serial_conn = SerialConnection(**config["robot"].pop("serial_connection"))

        self.robot = Robot(
            serial_connection=serial_conn,
            **config["robot"],
        )
        LOGGER.info("Config loaded")


if __name__ == "__main__":
    c = Config()
