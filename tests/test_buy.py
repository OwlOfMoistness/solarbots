import pytest
import brownie
from brownie import Wei, accounts, reverts, chain
import json

def test_buy_public(solar, mk, accounts, chain):
    for acc in accounts:
        acc.transfer(to=accounts[0], amount='100 ether')
    solar.updateYieldToken(mk, {'from':accounts[0]})

    with reverts('Public sale not ready'):
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)
    public_batch = solar.PUBLIC_SALE()
    with reverts('Wrong price'):
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 11})
    with reverts('Minting too many at once'):
        solar.mintBots(11, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})
    for i in range(public_batch // 10):
        print(i)
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    with reverts('Over public sale amount'):
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    big = accounts.at('0x0000000000000000000000000000000000000006', force=True)
    file = open('tests/merkle_test_whitelist.json', 'r')
    tree = json.load(file)
    accounts[0].transfer(to=big, amount=Wei('0.2 ether') * 8000)
    add_6_data = tree['claims'][big.address]
    solar.mintBotsWithSignature(add_6_data['index'], big, add_6_data['amount'], add_6_data['proof'], {'from':big, 'value': Wei('0.2 ether') * int(add_6_data['amount'])})

    time = solar.canPurchaseUnclaimed()
    now = chain.time()
    chain.sleep(time - now)

    for i in range(public_batch // 10):
        print(i)
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    with reverts("Can't mint over limit"):
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    pre = accounts[0].balance()
    solar.fetchEther({'from':accounts[0]})
    assert accounts[0].balance() - pre == '2000 ether'