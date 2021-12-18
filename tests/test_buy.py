import pytest
import brownie
from brownie import Wei, accounts, reverts, chain, web3
from eth_account.messages import encode_defunct
import json

def sign_msg(msg, pk):
    base_message = web3.soliditySha3(
            [ 'string' ] , 
            [msg])
    message = encode_defunct(base_message)
    # signer's pk
    sig = web3.eth.account.sign_message(message, pk)
    return sig


def test_buy_reserve(solar, mk, accounts, chain):
    for acc in accounts:
        acc.transfer(to=accounts[0], amount='100 ether')
    solar.updateYieldToken(mk, {'from':accounts[0]})

    with reverts('Public sale not ready'):
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)
    pks = accounts.from_mnemonic('noise just dawn civil drum cause crawl major episode same retreat divorce', count=30)
    sig = sign_msg('hi there!', pks[0].private_key)
    solar.meHuman('hi there!', sig.signature, {'from':pks[0]})
    solar.reserveBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})
    assert solar.reservedToMint(accounts[0]) == 10

    solar.transferMints(accounts[1], 10, {'from':accounts[0]})
    assert solar.reservedToMint(accounts[1]) == 10


def test_buy_public(solar, mk, accounts, chain):
    for acc in accounts:
        acc.transfer(to=accounts[0], amount='100 ether')
    solar.updateYieldToken(mk, {'from':accounts[0]})

    with reverts('Public sale not ready'):
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)
    public_batch = 1000
    with reverts('Wrong price'):
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 11})
    with reverts('Minting too many at once'):
        solar.mintBots(11, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})
    pks = accounts.from_mnemonic('noise just dawn civil drum cause crawl major episode same retreat divorce', count=30)
    sig = sign_msg('hi there!', pks[0].private_key)
    solar.meHuman('hi there!', sig.signature, {'from':pks[0]})
    for i in range(public_batch // 10):
        print(i)
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    # with reverts('Over public sale amount'):
    #     solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    big = accounts.at('0x861946AEB40036660Ea2C27C7ef0Ac36c81DB5eA', force=True)
    file = open('tests/merkle_test_whitelist.json', 'r')
    tree = json.load(file)
    accounts[0].transfer(to=big, amount=Wei('0.2 ether') * 8000)
    add_6_data = tree['claims'][big.address]
    solar.mintAllBotsWithSignature(add_6_data['index'], big, add_6_data['amount'], add_6_data['proof'], {'from':big, 'value': Wei('0.2 ether') * int(add_6_data['amount'])})

    # time = solar.publicSaleDate()
    # now = chain.time()
    # chain.sleep(time - now)

    for i in range(public_batch // 10 - 1):
        print(i)
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})
    solar.mintBots(9, {'from':accounts[0], 'value':Wei('0.2 ether') * 9})

    with reverts("Can't mint over limit"):
        solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})

    pre = accounts[0].balance()
    solar.fetchEther({'from':accounts[0]})
    assert accounts[0].balance() - pre == '1999.8 ether'