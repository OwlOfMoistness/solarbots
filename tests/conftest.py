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
    return SolarBots.deploy(1640127600, 1639840386, '0xa404fd424ef1f5e70d408d5b28dae6809f5246b20597fe2d53d5dce4590c5c6b', {'from':minter})

@pytest.fixture()
def mk(MkToken, solar, minter):
    return MkToken.deploy(solar, {'from':minter})