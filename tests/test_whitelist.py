import pytest
import brownie
from eth_account.messages import encode_defunct
from brownie import Wei, accounts, reverts, web3
import json

def test_whitelist(solar, accounts, chain):
    adds = [
        accounts[0].address, 
        accounts[1].address,
        accounts[2].address,
        accounts[3].address,
        accounts[4].address
    ]
    testers = accounts[:5]
    for test in testers:
        accounts[7].transfer(to=test, amount='20 ether')
    file = open('tests/merkle_test_whitelist.json', 'r')
    tree = json.load(file)
    add_0_data = tree['claims'][adds[0]]

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)

    solar.mintAllBotsWithSignature(add_0_data['index'], testers[0], add_0_data['amount'], add_0_data['proof'], {'from':testers[0], 'value': Wei('0.2 ether') * int(add_0_data['amount'])})
    assert solar.balanceOf(testers[0]) == 4
    with reverts('Claimed already'):
        solar.mintAllBotsWithSignature(add_0_data['index'], testers[0], add_0_data['amount'], add_0_data['proof'], {'from':testers[0], 'value': Wei('0.2 ether') * int(add_0_data['amount'])})

    add_1_data = tree['claims'][adds[1]]
    with reverts('Wrong proof'):
        solar.mintAllBotsWithSignature(add_1_data['index'], testers[1], add_1_data['amount'], add_0_data['proof'], {'from':testers[1], 'value': Wei('0.2 ether') * int(add_1_data['amount'])})
    solar.mintAllBotsWithSignature(add_1_data['index'], testers[1], add_1_data['amount'], add_1_data['proof'], {'from':testers[1], 'value': Wei('0.2 ether') * int(add_1_data['amount'])})
    assert solar.balanceOf(testers[1]) == 16

    add_2_data = tree['claims'][adds[2]]
    solar.mintAllBotsWithSignature(add_2_data['index'], testers[2], add_2_data['amount'], add_2_data['proof'], {'from':testers[2], 'value': Wei('0.2 ether') * int(add_2_data['amount'])})
    assert solar.balanceOf(testers[2]) == 40

    add_4_data = tree['claims'][adds[4]]
    solar.mintAllBotsWithSignature(add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * int(add_4_data['amount'])})
    assert solar.reservedToMint(adds[4]) == 100

def sign_msg(msg, pk):
    base_message = web3.soliditySha3(
            [ 'string' ] , 
            [msg])
    message = encode_defunct(base_message)
    # signer's pk
    sig = web3.eth.account.sign_message(message, pk)
    return sig

def test_buy_remainder(solar, mk, accounts, chain):
    solar.updateYieldToken(mk, {'from':accounts[0]})
    adds = [
        accounts[0].address, 
        accounts[1].address,
        accounts[2].address,
        accounts[3].address,
        accounts[4].address
    ]
    testers = accounts[:5]
    for test in testers:
        accounts[7].transfer(to=test, amount='20 ether')
    file = open('tests/merkle_test_whitelist.json', 'r')
    tree = json.load(file)
    add_4_data = tree['claims'][adds[4]]

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)
    solar.mintAllBotsWithSignature(add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * int(add_4_data['amount'])})
    assert solar.reservedToMint(adds[4]) == 100

    pks = accounts.from_mnemonic('noise just dawn civil drum cause crawl major episode same retreat divorce', count=30)
    with reverts('No human :('):
        solar.mintRemainder(10, {'from':testers[4]})
    sig = sign_msg('hi there!', pks[4].private_key)
    solar.meHuman('hi there!', sig.signature, {'from':testers[4]})

    for i in range(10):
        solar.mintRemainder(10, {'from':testers[4]})

    assert solar.balanceOf(testers[4]) == 400

    with reverts('Integer overflow'):
        solar.mintRemainder(1, {'from':testers[4]})

    add_2_data = tree['claims'][adds[2]]
    solar.mintAllBotsWithSignature(add_2_data['index'], testers[2], add_2_data['amount'], add_2_data['proof'], {'from':testers[2], 'value': Wei('0.2 ether') * int(add_2_data['amount'])})
    assert solar.balanceOf(testers[2]) == 40

    sig = sign_msg('hi there!', pks[1].private_key)
    solar.meHuman('hi there!', sig.signature, {'from':testers[1]})

    with reverts('Integer overflow'):
        solar.mintRemainder(1, {'from':testers[1]})

def test_mint_some_signatures(solar, mk, accounts, chain):
    solar.updateYieldToken(mk, {'from':accounts[0]})
    adds = [
        accounts[0].address, 
        accounts[1].address,
        accounts[2].address,
        accounts[3].address,
        accounts[4].address
    ]
    testers = accounts[:5]
    accounts[7].transfer(to=testers[4], amount='80 ether')
    file = open('tests/merkle_test_whitelist.json', 'r')
    tree = json.load(file)
    add_4_data = tree['claims'][adds[4]]

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)
    solar.mintSomeBotsWithSignature(100, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * int(add_4_data['amount'])})
    assert solar.reservedToMint(adds[4]) == 100
    with reverts("Can't mint more than allocated"):
        solar.mintSomeBotsWithSignature(50, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 50})

def test_mint_some_signatures_50(solar, mk, accounts, chain):
    solar.updateYieldToken(mk, {'from':accounts[0]})
    adds = [
        accounts[0].address, 
        accounts[1].address,
        accounts[2].address,
        accounts[3].address,
        accounts[4].address
    ]
    testers = accounts[:5]
    accounts[7].transfer(to=testers[4], amount='80 ether')
    file = open('tests/merkle_test_whitelist.json', 'r')
    tree = json.load(file)
    add_4_data = tree['claims'][adds[4]]

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)
    solar.mintSomeBotsWithSignature(50, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 50})
    assert solar.reservedToMint(adds[4]) == 50
    with reverts("Minted some"):
        solar.mintAllBotsWithSignature(add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * int(add_4_data['amount'])})
    solar.mintSomeBotsWithSignature(10, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 10})
    assert solar.balanceOf(adds[4]) == 40
    with reverts("Can't mint more than allocated"):
        solar.mintSomeBotsWithSignature(41, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 41})
    solar.mintSomeBotsWithSignature(40, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 40})
    assert solar.reservedToMint(adds[4]) == 90

def test_mint_some_signatures_random(solar, mk, accounts, chain):
    solar.updateYieldToken(mk, {'from':accounts[0]})
    adds = [
        accounts[0].address, 
        accounts[1].address,
        accounts[2].address,
        accounts[3].address,
        accounts[4].address
    ]
    testers = accounts[:5]
    accounts[7].transfer(to=testers[4], amount='80 ether')
    file = open('tests/merkle_test_whitelist.json', 'r')
    tree = json.load(file)
    add_4_data = tree['claims'][adds[4]]

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)
    solar.mintSomeBotsWithSignature(10, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 10})
    assert solar.balanceOf(adds[4]) == 40
    solar.mintSomeBotsWithSignature(11, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 11})
    assert solar.reservedToMint(adds[4]) == 11
    solar.mintSomeBotsWithSignature(9, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 9})
    solar.mintSomeBotsWithSignature(10, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 10})
    solar.mintSomeBotsWithSignature(10, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 10})
    solar.mintSomeBotsWithSignature(10, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 10})
    solar.mintSomeBotsWithSignature(10, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 10})
    solar.mintSomeBotsWithSignature(10, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 10})
    solar.mintSomeBotsWithSignature(10, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 10})
    solar.mintSomeBotsWithSignature(9, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 9})
    with reverts("Can't mint more than allocated"):
        solar.mintSomeBotsWithSignature(10, add_4_data['index'], testers[4], add_4_data['amount'], add_4_data['proof'], {'from':testers[4], 'value': Wei('0.2 ether') * 10})


