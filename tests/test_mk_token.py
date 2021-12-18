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


def test_issuance(solar, mk, chain):
    solar.updateYieldToken(mk, {'from':accounts[0]})
    solar.updateRewardLock(True, {'from':accounts[0]})
    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)

    pks = accounts.from_mnemonic('noise just dawn civil drum cause crawl major episode same retreat divorce', count=30)
    sig = sign_msg('hi there!', pks[0].private_key)
    solar.meHuman('hi there!', sig.signature, {'from':pks[0]})

    
    solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})
    chain.sleep(86400)
    chain.mine()
    rate = 6_849315068_000000000
    assert mk.getTotalClaimable(accounts[0]) >= 99 * rate * 40 / 100

    solar.getReward({'from':accounts[0]})

    assert mk.balanceOf(accounts[0]) >= 99 * rate * 40 / 100

def test_burn(solar, mk, chain):
    solar.updateYieldToken(mk, {'from':accounts[0]})
    solar.updateRewardLock(True, {'from':accounts[0]})
    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)

    pks = accounts.from_mnemonic('noise just dawn civil drum cause crawl major episode same retreat divorce', count=30)
    sig = sign_msg('hi there!', pks[0].private_key)
    solar.meHuman('hi there!', sig.signature, {'from':pks[0]})
    solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})
    chain.sleep(86400)
    chain.mine()
    rate = 6_849315068_000000000
    assert mk.getTotalClaimable(accounts[0]) >= 99 * rate * 40 / 100

    solar.getReward({'from':accounts[0]})

    assert mk.balanceOf(accounts[0]) >= 99 * rate * 40 / 100

    amount = mk.balanceOf(accounts[0])
    mk.burn('1 ether', {'from':accounts[0]})

    assert mk.balanceOf(accounts[0]) == amount - Wei('1 ether')

def test_burn_for(solar, mk, chain):
    solar.updateYieldToken(mk, {'from':accounts[0]})
    solar.updateRewardLock(True, {'from':accounts[0]})
    time = solar.publicSaleDate()
    now = chain.time()
    chain.sleep(time - now)

    pks = accounts.from_mnemonic('noise just dawn civil drum cause crawl major episode same retreat divorce', count=30)
    sig = sign_msg('hi there!', pks[0].private_key)
    solar.meHuman('hi there!', sig.signature, {'from':pks[0]})
    solar.mintBots(10, {'from':accounts[0], 'value':Wei('0.2 ether') * 10})
    chain.sleep(86400)
    chain.mine()
    rate = 6_849315068_000000000
    assert mk.getTotalClaimable(accounts[0]) >= 99 * rate * 40 / 100

    solar.getReward({'from':accounts[0]})

    assert mk.balanceOf(accounts[0]) >= 99 * rate * 40 / 100

    amount = mk.balanceOf(accounts[0])
    mk.approve(accounts[1], '2 ether', {'from':accounts[0]})
    mk.burnFor(accounts[0], '2 ether', {'from':accounts[1]})

    assert mk.balanceOf(accounts[0]) == amount - Wei('2 ether')

    with reverts('Integer overflow'):
        mk.burnFor(accounts[0], '2 ether', {'from':accounts[1]})