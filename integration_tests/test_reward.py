from .utils import wait_for_block, wait_for_new_blocks


def test_reward(cluster):
    # starts with cro1
    signer1_address = cluster.address("signer1", i=0)
    signer2_address = cluster.address("signer2", i=0)
    validator1_address = cluster.address("validator", i=0)
    validator2_address = cluster.address("validator", i=1)
    # starts with crocncl1
    validator1_operator_address = cluster.address("validator", i=0, bech="val")
    validator2_operator_address = cluster.address("validator", i=1, bech="val")
    signer1_old_balance = cluster.balance(signer1_address)
    amount_to_send = 2
    fees = 3_000_000_000
    # wait for initial reward processed, so that distribution values can be read
    wait_for_block(cluster, 2)
    old_commission_amount = cluster.distribution_commision(validator1_operator_address)
    old_commission_amount2 = cluster.distribution_commision(validator2_operator_address)
    old_community_amount = cluster.distribution_community()
    old_reward_amount = cluster.distribution_reward(validator1_address)
    old_reward_amount2 = cluster.distribution_reward(validator2_address)
    # transfer with fees
    cluster.transfer(
        signer1_address,
        signer2_address,
        f"{amount_to_send}basecro",
        fees=f"{fees}basecro",
    )
    # wait for fee reward receive
    wait_for_new_blocks(cluster, 2)
    signer1_balance = cluster.balance(signer1_address)
    assert signer1_balance + fees + amount_to_send == signer1_old_balance
    commission_amount = cluster.distribution_commision(validator1_operator_address)
    commission_amount2 = cluster.distribution_commision(validator2_operator_address)
    commission_amount_diff = (commission_amount - old_commission_amount) + (
        commission_amount2 - old_commission_amount2
    )
    community_amount = cluster.distribution_community()
    community_amount_diff = community_amount - old_community_amount
    reward_amount = cluster.distribution_reward(validator1_address)
    reward_amount2 = cluster.distribution_reward(validator2_address)
    reward_amount_diff = (reward_amount - old_reward_amount) + (
        reward_amount2 - old_reward_amount2
    )
    total_diff = commission_amount_diff + community_amount_diff + reward_amount_diff
    minted_value = total_diff - fees
    # these values are generated by minting
    # if there is system-overload, minted_value can be larger than expected
    # fee is computed at EndBlock, AllocateTokens
    # commission = proposerReward * proposerCommissionRate
    # communityFunding = feesCollectedDec * communityTax
    # poolReceived = feesCollectedDec - proposerReward - communityFunding
    assert 77000.0 <= minted_value <= 233937.0