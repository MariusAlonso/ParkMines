
import pytest
from pytest_mock import *
from inputs import *
import datetime

def test_returns_a_list(mocker):
    mocker.patch("sys.argv", ["pytest", "--path", "inputs/movements.csv"])
    result = importFromFile()

    assert type(result) == list

def test_vehicle_1():
    vehicle_1 = importFromFile()[0]
    print(vehicle_1)

    assert type(vehicle_1.deposit) == datetime.datetime
    assert type(vehicle_1.retrieval) == datetime.datetime
    assert type(vehicle_1.order_deposit) == datetime.datetime
    assert type(vehicle_1.order_retrieval) ==  datetime.datetime