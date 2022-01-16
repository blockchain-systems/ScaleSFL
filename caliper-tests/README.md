# Caliper Tests

This tests the sharding performance of the consensus mechanism, using [hyperledger caliper](https://github.com/hyperledger/caliper). Sample benchmarks can be found in [caliper-benchmarks](https://github.com/hyperledger/caliper-benchmarks)

First install the dependencies

```sh
yarn
```

If you need to change the fabric version (from 2.1.0), bind caliper to the version of Fabric being used

```sh
npx caliper bind --caliper-bind-sut fabric:2.1.0
```

If you use a caliper created SUT, you will also need to generate the crypto configuration. We use the test-network so this is not needed

```sh
cd networks/fabric/config_solo_raft

./generate.sh
```

Note: since we are using a CA, you may have to update the network file `networks/fabric-config.yaml` with the correct secret key path, e.g.

```sh
ls -la ../test-network/organizations/peerOrganizations/org*.example.com/users/User1@org*.example.com/msp/keystore
```

```sh
cd $CALIPER_FOLDER_ROOT

npx caliper launch manager \
    --caliper-workspace . \
    --caliper-benchconfig benchmarks/config.yaml \
    --caliper-networkconfig networks/fabric-config.yaml \
    --caliper-flow-only-test \
    --caliper-fabric-gateway-enabled
```
