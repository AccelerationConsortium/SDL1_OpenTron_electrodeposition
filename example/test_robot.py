from unittest.mock import MagicMock
import time
import pytest
from _pytest.monkeypatch import MonkeyPatch
import serial
from python.ardu import Arduino
from python.config import Config


@pytest.fixture(
    autouse=True
)  # set this to false if you want to actually connect to the robot
def _mock_serial(monkeypatch: MonkeyPatch):
    # use this fixture to mock the serial connection
    monkeypatch.setattr(
        serial, "Serial", MagicMock(serial.Serial, create_autospec=True)
    )


@pytest.fixture(autouse=True)  # this will skip the sleep time
def _shorten_wait(monkeypatch: MonkeyPatch):
    def mock_sleep(loadtime):
        pass

    monkeypatch.setattr(time, "sleep", mock_sleep)


def test_robot():
    """Test the robot class"""
    robot = Arduino(config=Config().robot)
    robot.set_temperature(26.0)
    for i in [7, 8]:
        robot.pump(i, 2, 1, 1)
        robot.pump(i, 2, 1, 2)
    with pytest.raises(ValueError):
        robot.pump(9, 2, 1, 1)
