
import pytest
from pytest_mock import *
from inputs import *
import datetime

def test_returns_a_list(mocker):
    mocker.patch("sys.argv", ["pytest", "--path", "inputs/movements.csv"])
    result = import_from_file()

    assert type(result) == list

def test_vehicle_1():
    vehicle_1 = import_from_file()[0]
    print(vehicle_1)

    assert vehicle_1.deposit == datetime.datetime(2019, 9, 1, 7, 25, 22)
    assert vehicle_1.retrieval == datetime.datetime(2019, 9, 6, 8, 52, 40)
    assert vehicle_1.order_deposit == datetime.datetime(2019, 9, 1, 7, 25, 22)
    assert vehicle_1.order_retrieval ==  datetime.datetime(2019, 9, 6, 8, 52, 40)