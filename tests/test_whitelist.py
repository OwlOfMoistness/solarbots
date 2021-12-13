import pytest
import brownie
from brownie import Wei, accounts, reverts
import json

def test_whitelist(solar, accounts, chain):
    adds = [
        '0x0000000000000000000000000000000000000001', 
        '0x0000000000000000000000000000000000000002',
        '0x0000000000000000000000000000000000000003',
        '0x0000000000000000000000000000000000000004',
        '0x0000000000000000000000000000000000000005'
    ]
    testers = [accounts.at(add, force=True) for add in adds]
    for test in testers:
        accounts[0].transfer(to=test, amount='20 ether')
    file = open('tests/merkle_test_whitelist.json', 'r')
    tree = json.load(file)
    add_0_data = tree['claims'][adds[0]]

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)

    solar.mintBotsWithSignature(add_0_data['index'], testers[0], add_0_data['amount'], add_0_data['proof'], {'from':testers[0], 'value': Wei('0.2 ether') * int(add_0_data['amount'])})
    assert solar.balanceOf(testers[0]) == 4
    with reverts('Claimed already'):
        solar.mintBotsWithSignature(add_0_data['index'], testers[0], add_0_data['amount'], add_0_data['proof'], {'from':testers[0], 'value': Wei('0.2 ether') * int(add_0_data['amount'])})

    add_1_data = tree['claims'][adds[1]]
    with reverts('Wrong proof'):
        solar.mintBotsWithSignature(add_1_data['index'], testers[1], add_1_data['amount'], add_0_data['proof'], {'from':testers[1], 'value': Wei('0.2 ether') * int(add_1_data['amount'])})
    solar.mintBotsWithSignature(add_1_data['index'], testers[1], add_1_data['amount'], add_1_data['proof'], {'from':testers[1], 'value': Wei('0.2 ether') * int(add_1_data['amount'])})
    assert solar.balanceOf(testers[1]) == 16

    add_2_data = tree['claims'][adds[2]]
    solar.mintBotsWithSignature(add_2_data['index'], testers[2], add_2_data['amount'], add_2_data['proof'], {'from':testers[2], 'value': Wei('0.2 ether') * int(add_2_data['amount'])})
    assert solar.balanceOf(testers[2]) == 40

    add_4_data = tree['claims'][adds[4]]
    solar.mintBotsWithSignature(add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * int(add_4_data['amount'])})
    assert solar.reservedToMint(adds[4]) == 100

def test_buy_remainder(solar, mk, accounts, chain):
    solar.updateYieldToken(mk, {'from':accounts[0]})
    adds = [
        '0x0000000000000000000000000000000000000001', 
        '0x0000000000000000000000000000000000000002',
        '0x0000000000000000000000000000000000000003',
        '0x0000000000000000000000000000000000000004',
        '0x0000000000000000000000000000000000000005'
    ]
    testers = [accounts.at(add, force=True) for add in adds]
    for test in testers:
        accounts[0].transfer(to=test, amount='20 ether')
    file = open('tests/merkle_test_whitelist.json', 'r')
    tree = json.load(file)
    add_4_data = tree['claims'][adds[4]]

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)
    solar.mintBotsWithSignature(add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * int(add_4_data['amount'])})
    assert solar.reservedToMint(adds[4]) == 100

    for i in range(10):
        solar.mintRemainder(10, {'from':testers[4]})

    assert solar.balanceOf(testers[4]) == 400

    with reverts('Integer overflow'):
        solar.mintRemainder(1, {'from':testers[4]})

    add_2_data = tree['claims'][adds[2]]
    solar.mintBotsWithSignature(add_2_data['index'], testers[2], add_2_data['amount'], add_2_data['proof'], {'from':testers[2], 'value': Wei('0.2 ether') * int(add_2_data['amount'])})
    assert solar.balanceOf(testers[2]) == 40

    with reverts('Integer overflow'):
        solar.mintRemainder(1, {'from':testers[1]})
