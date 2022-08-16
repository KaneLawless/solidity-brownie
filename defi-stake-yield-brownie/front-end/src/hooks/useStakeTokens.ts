import { useEffect, useState } from "react"
import { useContractFunction, useEthers } from "@usedapp/core"
import TokenFarm from "../chain-info/contracts/TokenFarm.json"
import ERC20 from "../chain-info/contracts/MockDai.json"
import networkMapping from "../chain-info/deployments/map.json"
import { constants, utils } from "ethers"
import { Contract } from "@ethersproject/contracts"


export const useStakeTokens = (tokenAddress: string) => {
    // address
    // abi
    // chain Id
    const { chainId } = useEthers()
    const stringChainId = String(chainId)

    // TokenFarm Contract
    const { abi } = TokenFarm
    const tokenFarmAddress = chainId ? networkMapping[stringChainId]["TokenFarm"][0] : constants.AddressZero
    const tokenFarmInterface = new utils.Interface(abi)
    const tokenFarmContract = new Contract(tokenFarmAddress, tokenFarmInterface)

    // Token Contract
    const erc20Abi = ERC20.abi
    const erc20Interface = new utils.Interface(erc20Abi)
    const erc20Contract = new Contract(tokenAddress, erc20Interface)

    // Approve
    const { send: erc20ApproveSend, state: approveAndStakeErc20State } = useContractFunction(erc20Contract, "approve",
        { transactionName: "Approve ERC20 Transfer" })

    const approveAndStake = (amount: string) => {
        setAmountToStake(amount)
        return erc20ApproveSend(tokenFarmAddress, amount)
    }

    const { send: stakeSend, state: stakeState } =
        useContractFunction(tokenFarmContract, "stakeTokens",
            {
                transactionName: "Stake tokens"
            })


    const [amountToStake, setAmountToStake] = useState("0")

    // If something in the array changes, execute function
    useEffect(() => {
        if (approveAndStakeErc20State.status === "Success") {
            // stake
            stakeSend(amountToStake, tokenAddress)
        }
    }, [approveAndStakeErc20State, amountToStake, tokenAddress])


    const [state, setState] = useState(approveAndStakeErc20State)

    useEffect(() => {
        if (approveAndStakeErc20State.status === "Success") {
            setState(stakeState)
        } else {
            setState(approveAndStakeErc20State)
        }
    }, [approveAndStakeErc20State, stakeState])

    return { approveAndStake, state }
}