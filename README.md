# Sharded Committee Consensus for Blockchain based Federated Learning

In this project we implement the [committee consensus](https://arxiv.org/pdf/2004.00773.pdf) within [Hyperledger Fabric](https://www.hyperledger.org/use/fabric). We extend this algorithm to include a sharding mechanism. This allows for further scalability, and capacity of the network. We test our approach using [Hyperledger Caliper](https://www.hyperledger.org/use/caliper), a benchmarking tool.

## Getting Started

This project relies on several componenets to test. The first step is to bring up the test network to bring up the Fabric blockchain

```sh
.test-network/network.sh up
```
