# Exit on error
set -e

starttime=$(date +%s)

# Bring network up
./network.sh down # remove any containers from previous runs (optional)
./network.sh up -ca

# Create channels
./network.sh createChannel -c mainline
./network.sh createChannel -c shard1

# Deploy chaincode 
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

export PATH=$(realpath ${PWD}/../bin):$PATH
export FABRIC_CFG_PATH=$(realpath ${PWD}/../config/)

# Set peer as org1
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

# init mainline ledger
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

# init shard ledger 
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

echo "Setup time: $(($(date +%s) - starttime))s"