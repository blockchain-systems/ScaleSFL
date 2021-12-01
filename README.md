# Sharded Committee Consensus for Blockchain based Federated Learning

In this project we implement the [committee consensus](https://arxiv.org/pdf/2004.00773.pdf) within [Hyperledger Fabric](https://www.hyperledger.org/use/fabric). We extend this algorithm to include a sharding mechanism. This allows for further scalability, and capacity of the network. We test our approach using [Hyperledger Caliper](https://www.hyperledger.org/use/caliper), a benchmarking tool.

## Getting Started

### Prerequisites

Make sure you have the proper [prerequisites](https://hyperledger-fabric.readthedocs.io/en/release-2.2/prereqs.html)  
To get the binaries required to run the project, you can run the command

```sh
curl -fsSL https://raw.githubusercontent.com/hyperledger/fabric/master/scripts/bootstrap.sh | bash -s
```

Next check the commands available by running

```sh
cd test-network
./network.sh -h
```

### Running the network

This project relies on several componenets to test. The first step is to bring up the test network to bring up the Fabric blockchain. This is based n the test-network provided by [fabric-samples](https://github.com/hyperledger/fabric-samples)

```sh
./network.sh down # remove any containers from previous runs (optional)
./network.sh up -ca
```

To create a channel we can use the following command

```sh
./network.sh createChannel -c mainline
./network.sh createChannel -c shard1
```

Next we'll deploy the model catalyst chaincode to in using

```sh
./network.sh deployCC \
    -c mainline \
    -ccn catalyst \
    -ccp ../chaincode/catalyst \
    -ccl typescript

./network.sh deployCC \
    -c shard1 \
    -ccn models \
    -ccp ../chaincode/shard \
    -ccl typescript
```

where `-c` is the channel name  
`-ccn` is the chaincode name  
`-ccp` is the chaincode path, and  
`-ccl` is the chaincode language

Next make sure you the binaries are in your path

```sh
export PATH=$(realpath ${PWD}/../bin):$PATH
```

and set the config directory

```sh
export FABRIC_CFG_PATH=$(realpath ${PWD}/../config/)
```

Next we can invoke the chaincode using (only set one peer at a time)

```sh
# Org1 env variables
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

# Org2 env variables
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org2MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
export CORE_PEER_ADDRESS=localhost:9051
```

We can check which channels a peer is in using

```sh
peer channel list
```

Next invoke the chaincode by calling

```sh
peer chaincode invoke \
    -n catalyst \
    -C mainline \
    -o localhost:7050 \
    --tls \
    --ordererTLSHostnameOverride orderer.example.com \
    --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
    --peerAddresses localhost:7051 \
    --peerAddresses localhost:9051 \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
    -c '{"function":"InitLedger","Args":[]}'
```

```sh
peer chaincode invoke \
    -n models \
    -C shard1 \
    -o localhost:7050 \
    --tls \
    --ordererTLSHostnameOverride orderer.example.com \
    --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
    --peerAddresses localhost:7051 \
    --peerAddresses localhost:9051 \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
    -c '{"function":"InitLedger","Args":[]}'
```

Now query the chaincode, we'll get all shards using

```sh
peer chaincode query -C mainline -n catalyst -c '{"Args":["GetAllShardss"]}'
```

---

Now transfer an asset by

```sh
peer chaincode invoke \
    -n basic \
    -C mainline \
    -o localhost:7050 \
    --tls \
    --ordererTLSHostnameOverride orderer.example.com \
    --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
    --peerAddresses localhost:7051 \
    --peerAddresses localhost:9051 \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
    -c '{"function":"TransferAsset","Args":["asset6","Christopher"]}'
```

The endorsement policy for chaincode requires transactions be signed by both Org1 and Org2, so the invoke command must target both peers (using --peerAddresses)

Switching to Org2 env, and running

```sh
peer chaincode query -C mainline -n basic -c '{"Args":["ReadAsset","asset6"]}'
```

will show the asset has been transferred to "Christopher"

---

Finally make sure to bring down the network

```sh
./network.sh down
```
