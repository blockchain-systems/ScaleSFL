# Exit on error
set -e

# Config
num_shards=3
main_chain_channel="mainline"
shards_channel_prefix="shard"
task_chaincode_name="catalyst"
shard_chaincode_name="models"
task_chaincode="../chaincode/catalyst"
shard_chaincode="../chaincode/shard"

# Script Metrics
starttime=$(date +%s)

# Bring network up
./network.sh down # remove any containers from previous runs (optional)
./network.sh up -ca

# Create channels
./network.sh createChannel -c $main_chain_channel
for i in `seq 0 $(($num_shards - 1))`; do
    ./network.sh createChannel -c $shards_channel_prefix$i
done

pushd ./addOrg3
./addOrg3.sh up -ca -c $main_chain_channel
for i in `seq 0 $(($num_shards - 1))`; do
    ./addOrg3.sh up -ca -c $shards_channel_prefix$i
done
popd

# Deploy chaincode 
./network.sh deployCC \
    -c $main_chain_channel \
    -ccn $task_chaincode_name \
    -ccp $task_chaincode \
    -ccl typescript
for i in `seq 0 $(($num_shards - 1))`; do
    ./network.sh deployCC \
        -c $shards_channel_prefix$i \
        -ccn $shard_chaincode_name$i \
        -ccp $shard_chaincode \
        -ccl typescript
done

export PATH=$(realpath ${PWD}/../bin):$PATH
export FABRIC_CFG_PATH=$(realpath ${PWD}/../config/)

# Set peer as org1
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

# init mainchain ledger
peer chaincode invoke \
    -n $task_chaincode_name \
    -C $main_chain_channel \
    -o localhost:7050 \
    --tls \
    --ordererTLSHostnameOverride orderer.example.com \
    --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
    --peerAddresses localhost:7051 \
    --peerAddresses localhost:9051 \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
    -c '{"function":"InitLedger","Args":[]}'

# init shard ledger 
for i in `seq 0 $(($num_shards - 1))`; do
    peer chaincode invoke \
        -n $shard_chaincode_name$i \
        -C $shards_channel_prefix$i \
        -o localhost:7050 \
        --tls \
        --ordererTLSHostnameOverride orderer.example.com \
        --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
        --peerAddresses localhost:7051 \
        --peerAddresses localhost:9051 \
        --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
        --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
        -c '{"function":"InitLedger","Args":[]}'
done

echo "Setup time: $(($(date +%s) - starttime))s"