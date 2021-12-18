import pytest
import csv

@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass

@pytest.fixture()
def minter(accounts):
    return accounts[0]


@pytest.fixture()
def solar(SolarBots, minter,):
    return SolarBots.deploy(1640023200, 1640199600, '0xa95c3ab33bf64b2f2b2a1b925a867f8bc965d2f7ef0b3094bbbb68cdbab1101b', {'from':minter})

@pytest.fixture()
def mk(MkToken, solar, minter):
    return MkToken.deploy(solar, {'from':minter})