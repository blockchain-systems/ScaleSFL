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
        --caliper-benchconfig benchmarks/model-creation.yaml \
        --caliper-networkconfig networks/fabric-config.yaml \
        --caliper-progress-reporting-interval 2000 \
        --caliper-flow-only-test \
        --caliper-worker-pollinterval 250 \
        --caliper-fabric-gateway-enabled
```

## Notes

When setting up tests with multiple independent channels, for example

```
channels
├── mainline
│   ├── org1
│   ├── org2
│   └── org3
├── shard0
│   └── org1
├── shard1
│   └── org2
├── shard2
│   └── org3
```

service discovery fails. Because of this we can manually define the network configurations using [connection profiles](https://hyperledger-fabric.readthedocs.io/en/latest/developapps/connectionprofile.html) and disable service discovery.

for example we could add channels and orderers to the templated connection profiles

```yaml
channels:
    mainline:
        orderers:
            - orderer.example.com
        peers:
            peer0.org1.example.com:
                eventSource: true
            peer0.org2.example.com:
                eventSource: true
            peer0.org3.example.com:
                eventSource: true
    shard0:
        orderers:
            - orderer.example.com
        peers:
            peer0.org1.example.com:
                eventSource: true
```

```yaml
orderers:
    orderer.example.com:
        url: grpcs://localhost:7050
        grpcOptions:
            ssl-target-name-override: orderer.example.com
        tlsCACerts:
            path: "../test-network/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"
```

Make sure to add the other peer definitions in each connection profile as well.

Additionally there seems to be a bug in the benchmark [rate controllers](https://hyperledger.github.io/caliper/v0.4.2/rate-controllers/) for `fixed-feedback-rate`, so be sure to experiment with other controllers.

Another bug in Caliper that seems to cause failures sometimes when all workers do not exit, usually caused if the requests are long running as we are experiencing for these tests. If this happens try to limit the workers such that they match the number of shards.
