# Caliper Tests

This tests the sharding performance of the consensus mechanism, using [hyperledger caliper](https://github.com/hyperledger/caliper). Sample benchmarks can be found in [caliper-benchmarks](https://github.com/hyperledger/caliper-benchmarks)

First install the dependencies

```sh
yarn
```

Now we need to bind caliper to a version of Fabric being used

```sh
npx caliper bind --caliper-bind-sut fabric:2.1.0
```

You will also need to generate the crypto configuration

```sh
cd networks/fabric/config_solo_raft

./generate.sh
```

```sh
cd ../../..

npx caliper launch manager \
    --caliper-workspace . \
    --caliper-benchconfig benchmarks/config.yaml \
    --caliper-networkconfig networks/fabric-config.yaml \
    --caliper-flow-only-test \
    --caliper-fabric-gateway-enabled
```
