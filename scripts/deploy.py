import pytest
import brownie
from brownie import Wei, accounts, chain, SolarBots, MkToken, accounts
import json

def deploy():
	user = accounts.load('moist', '\0')

	public_sale = 1639481593
	remainder = 1640000000
	solar = SolarBots.deploy(remainder, public_sale, '0xa6f5a10bfe034e9ca837611a33de415727b3b114a591226882443fd4f1f9cfae', {'from':user}, publish_source=False)
	mk = MkToken.deploy(solar, {'from':user}, publish_source=False)
	solar.updateYieldToken(mk, {'from':user})
	solar.mintBots(1, {'from':user, 'value':'0.2 ether'})