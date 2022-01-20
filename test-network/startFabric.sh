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
./network.sh up -ca -orgs 1,2,3

# Create channels
./network.sh createChannel -c $main_chain_channel -orgs 1,2,3
for i in `seq 0 $(($num_shards - 1))`; do
    ./network.sh createChannel -c $shards_channel_prefix$i -orgs $((i + 1))
done

# Deploy chaincode 
./network.sh deployCC \
    -c $main_chain_channel \
    -ccn $task_chaincode_name \
    -ccp $task_chaincode \
    -ccl typescript \
    -orgs 1,2,3
for i in `seq 0 $(($num_shards - 1))`; do
    ./network.sh deployCC \
        -c $shards_channel_prefix$i \
        -ccn $shard_chaincode_name$i \
        -ccp $shard_chaincode \
        -ccl typescript \
        -orgs $((i + 1))
done

export PATH=$(realpath ${PWD}/../bin):$PATH
export FABRIC_CFG_PATH=$(realpath ${PWD}/../config/)

# Set peer as org1
. scripts/envVar.sh
setGlobals 1

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
    --peerAddresses localhost:11051 \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
    --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/ca.crt \
    -c '{"function":"InitLedger","Args":[]}'

# init shard ledger 
for i in `seq 0 $(($num_shards - 1))`; do
    setGlobals $(($i + 1))
    peer chaincode invoke \
        -n $shard_chaincode_name$i \
        -C $shards_channel_prefix$i \
        -o localhost:7050 \
        --tls \
        --ordererTLSHostnameOverride orderer.example.com \
        --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
        --peerAddresses $CORE_PEER_ADDRESS \
        --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org$((i + 1)).example.com/peers/peer0.org$((i + 1)).example.com/tls/ca.crt \
        -c '{"function":"InitLedger","Args":[]}'
done

echo "Setup time: $(($(date +%s) - starttime))s"