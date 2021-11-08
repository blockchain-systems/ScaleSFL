
## Network Overview

After we have set up a series of TLS and ECert CA services, we'll use the CAs to generate 
[Local MSP](https://hyperledger-fabric.readthedocs.io/en/latest/membership/membership.html#local-msps) structures for 
all of the nodes, using the local MSPs to launch our network peers and orderers.


### TL/DR : 

```shell
./network up 
... 
✅ - Creating local node MSP ...
✅ - Launching orderers ...
✅ - Launching peers ...
🏁 - Network is ready.
```

## Fabric MSP Context 

Before we launch the network peers and orderers, each node in the network needs to have available: 

- TLS Root Certificates for all organizations in the network
- TLS Certificates and Signing Keys for SSL server/hostname verification of the network node
- Enrollment Certificates validating the network node identity (local MSP)
- Enrollment Certificates for an `Admin` identity / role for the organization. 

In order to create the local node MSP, we must first register and enroll the node identities with the ECert CAs, and
then organize the TLS and MSP certificates into a location suitable for launching the network services.

The key steps in this process are: 

- [Registering and enrolling identities with a CA](https://hyperledger-fabric-ca.readthedocs.io/en/latest/deployguide/use_CA.html#registering-and-enrolling-identities-with-a-ca)
- [Create the local MSP of a node](https://hyperledger-fabric-ca.readthedocs.io/en/latest/deployguide/use_CA.html#create-the-local-msp-of-a-node)

In the test network, each organization includes a function that wraps the registration, enrollment, and MSP aggregation 
into a series of fabric-ca-client calls.  [The script](../scripts/test_network.sh) will be executed directly on the 
org's ECert CA pod, with access to the persistent volume for storage of the MSP and TLS certificates.  While this is 
largely boilerplate scripting, the process is straightforward:  For each node in the network, we'll use the CAs to 
generate TLS+MSP certificates, bundling into an MSP with a `config.yaml` specifying the fabric roles associated with 
the target usage in the network. 

For example, the ordering organization sets up the node local MSP with: 
```shell
# Each identity in the network needs a registration and enrollment.
fabric-ca-client register --id.name org0-orderer1 --id.secret ordererpw --id.type orderer --url https://org0-ecert-ca --mspdir $FABRIC_CA_CLIENT_HOME/org0-ecert-ca/rcaadmin/msp
fabric-ca-client register --id.name org0-orderer2 --id.secret ordererpw --id.type orderer --url https://org0-ecert-ca --mspdir $FABRIC_CA_CLIENT_HOME/org0-ecert-ca/rcaadmin/msp
fabric-ca-client register --id.name org0-orderer3 --id.secret ordererpw --id.type orderer --url https://org0-ecert-ca --mspdir $FABRIC_CA_CLIENT_HOME/org0-ecert-ca/rcaadmin/msp
fabric-ca-client register --id.name org0-admin --id.secret org0adminpw  --id.type admin   --url https://org0-ecert-ca --mspdir $FABRIC_CA_CLIENT_HOME/org0-ecert-ca/rcaadmin/msp --id.attrs "hf.Registrar.Roles=client,hf.Registrar.Attributes=*,hf.Revoker=true,hf.GenCRL=true,admin=true:ecert,abac.init=true:ecert"

fabric-ca-client enroll --url https://org0-orderer1:ordererpw@org0-ecert-ca --csr.hosts org0-orderer1 --mspdir /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer1.org0.example.com/msp
fabric-ca-client enroll --url https://org0-orderer2:ordererpw@org0-ecert-ca --csr.hosts org0-orderer2 --mspdir /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer2.org0.example.com/msp
fabric-ca-client enroll --url https://org0-orderer3:ordererpw@org0-ecert-ca --csr.hosts org0-orderer3 --mspdir /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer3.org0.example.com/msp
fabric-ca-client enroll --url https://org0-admin:org0adminpw@org0-ecert-ca --mspdir /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/users/Admin@org0.example.com/msp

# Each node in the network needs a TLS registration and enrollment.
fabric-ca-client register --id.name org0-orderer1 --id.secret ordererpw --id.type orderer --url https://org0-tls-ca --mspdir $FABRIC_CA_CLIENT_HOME/tls-ca/tlsadmin/msp
fabric-ca-client register --id.name org0-orderer2 --id.secret ordererpw --id.type orderer --url https://org0-tls-ca --mspdir $FABRIC_CA_CLIENT_HOME/tls-ca/tlsadmin/msp
fabric-ca-client register --id.name org0-orderer3 --id.secret ordererpw --id.type orderer --url https://org0-tls-ca --mspdir $FABRIC_CA_CLIENT_HOME/tls-ca/tlsadmin/msp

fabric-ca-client enroll --url https://org0-orderer1:ordererpw@org0-tls-ca --csr.hosts org0-orderer1 --mspdir /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer1.org0.example.com/tls
fabric-ca-client enroll --url https://org0-orderer2:ordererpw@org0-tls-ca --csr.hosts org0-orderer2 --mspdir /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer2.org0.example.com/tls
fabric-ca-client enroll --url https://org0-orderer3:ordererpw@org0-tls-ca --csr.hosts org0-orderer3 --mspdir /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer3.org0.example.com/tls

# Copy the TLS signing keys to a fixed path for convenience when starting the orderers.
cp /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer1.org0.example.com/tls/keystore/*_sk /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer1.org0.example.com/tls/keystore/server.key
cp /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer2.org0.example.com/tls/keystore/*_sk /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer2.org0.example.com/tls/keystore/server.key
cp /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer3.org0.example.com/tls/keystore/*_sk /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer3.org0.example.com/tls/keystore/server.key

# Create an MSP config.yaml (why is this not generated by the enrollment by fabric-ca-client?)
echo "NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/org0-ecert-ca.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/org0-ecert-ca.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/org0-ecert-ca.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/org0-ecert-ca.pem
    OrganizationalUnitIdentifier: orderer" > /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer1.org0.example.com/msp/config.yaml

cp /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer1.org0.example.com/msp/config.yaml /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer2.org0.example.com/msp/config.yaml
cp /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer1.org0.example.com/msp/config.yaml /var/hyperledger/fabric/organizations/ordererOrganizations/org0.example.com/orderers/org0-orderer3.org0.example.com/msp/config.yaml
```


## External Chaincode Builders 

Running Fabric in Kubernetes places some unique constraints on the Chaincode lifecycle: 

- Many cloud-native vendors rely on [containerd.io](https://containerd.io) to manage the lifecycle of containers 
  within a cluster.  By contrast, Fabric assumes the presence of a Docker daemon to compile and launch chaincode 
  containers.  Without a local Docker daemon, Fabric's default chaincode pipeline is doomed! 
  

- For security and operational concerns, it is a "non-starter" to run a docker daemon on Kubernetes worker nodes.


- For cloud-ready development, test, validation, CI/CD, and production practices, the use of the 
  [Chaincode as a Service](https://hyperledger-fabric.readthedocs.io/en/latest/cc_service.html) pattern provides a 
  _vastly superior user experience_.  However, with the current (2.3) Fabric builds, the configuration of [External 
  Chaincode Builders](https://hyperledger-fabric.readthedocs.io/en/latest/cc_launcher.html) is non-trivial and 
  includes some real complexity for deployment to Kubernetes.
  

- Running Chaincode builds in Docker in Docker, running in Kubernetes in Docker is ... interesting.  Let's 
  step back and _keep it simple_. 


  
For the Kube Test Network, we've configured the peer nodes to launch with the [fabric-ccs-builder](https://github.com/hyperledgendary/fabric-ccs-builder) 
External Chaincode Builders pre-bundled into the network.  When chaincode is installed on the peers, the external 
builder binaries will be invoked, bypassing the reliance on a local Docker daemon running in Kubernetes.

This configuration is accomplished by registering an external builder in the peer core.yaml: 

```yaml
    externalBuilders:
      - path: /var/hyperledger/fabric/chaincode/ccs-builder
        name: ccs-builder
        propagateEnvironment:
          - HOME
          - CORE_PEER_ID
          - CORE_PEER_LOCALMSPID
```
  
At launch time, the Kubernetes deployment includes an init container that will load the fabric-ccs-builder binaries 
from a public container registry, copying the external builders into the target volume in the peer: 

```yaml
      initContainers:
        - name: fabric-ccs-builder
          image: {{LOCAL_CONTAINER_REGISTRY}}/fabric-ccs-builder
          command: [sh, -c]
          args: ["cp /go/bin/* /var/hyperledger/fabric/chaincode/ccs-builder/bin/"]
          volumeMounts:
            - name: ccs-builder
              mountPath: /var/hyperledger/fabric/chaincode/ccs-builder/bin
```

With this configuration we eliminate the reliance on Docker daemon, fully supporting the _Chaincode-as-a-Service_ 
pattern for building smart contracts in a cloud-native environment.

- [x] Pro tip: Use the companion container registry at `localhost:5000` to deploy custom chaincode into the test network. 
- [x] Pro tip: Deploy a chaincode with `address: host.docker.internal:9999` and run your chaincode in a debugger. 
- [ ] Note: An external chaincode builder will be included in future releases of Fabric.


## Starting Peers and Orderers 

```shell
✅ - Launching orderers ...
✅ - Launching peers ...
```

Once the local MSP structures for the network nodes have been created, the orderers and peers may be launched in the 
namespace.  System nodes will read base configuration files (orderer.yaml and core.yaml) from the organization 
config folder, made available in Kubernetes as the `fabric-config${org}` config map.

Each orderer and peer creates one `Deployment`, `Pod`, and `Service` in the namespace.  In addition, each org 
defines an `orgN-peerM-config` `ConfigMap` with environment variable overrides replacing the default settings 
in the core.yaml file.  Note that each node's [environment](../kube/org1/org1-peer1.yaml) includes pointers to the 
node local MSP folders, certificates, and TLS signing keys that we generated above.

Note that the deployment yaml files include some basic template substitution and parameters.  For simplicity and 
clarity, we elected to use basic string substitution with sed/awk/bash/etc., rather than introduce a Kube template 
binding system (e.g. Helm, Kustomize, Kapitan, Ansible, etc.) for manipulating yaml templates:  

```shell
cat kube/org0/org0-orderer1.yaml | sed 's,{{FABRIC_VERSION}},'${FABRIC_VERSION}',g' | kubectl -n $NS -f - 
cat kube/org0/org0-orderer2.yaml | sed 's,{{FABRIC_VERSION}},'${FABRIC_VERSION}',g' | kubectl -n $NS -f - 
cat kube/org0/org0-orderer3.yaml | sed 's,{{FABRIC_VERSION}},'${FABRIC_VERSION}',g' | kubectl -n $NS -f - 

# Wait for the orderers to completely start before launching the network peer nodes. 
kubectl -n $NS rollout status deploy/org0-orderer1 
kubectl -n $NS rollout status deploy/org0-orderer2 
kubectl -n $NS rollout status deploy/org0-orderer3

cat kube/org1/org1-peer1.yaml | sed 's,{{FABRIC_VERSION}},'${FABRIC_VERSION}',g' | kubectl -n $NS -f - 
cat kube/org1/org1-peer2.yaml | sed 's,{{FABRIC_VERSION}},'${FABRIC_VERSION}',g' | kubectl -n $NS -f - 
cat kube/org2/org2-peer1.yaml | sed 's,{{FABRIC_VERSION}},'${FABRIC_VERSION}',g' | kubectl -n $NS -f - 
cat kube/org2/org2-peer2.yaml | sed 's,{{FABRIC_VERSION}},'${FABRIC_VERSION}',g' | kubectl -n $NS -f - 
```

- [x] Pro tip: Run an early-release Fabric build by setting `TEST_NETWORK_FABRIC_VERSION=2.4.0-beta`


## Next Steps :

After the peers and orderers have started, the Kube namespace includes pods, deployments, and service bindings for: 

- Org0 (org0.example.com): 
  - TLS Certificate Authority : https://org0-tls-ca
  - ECert Certificate Authority : https://org0-ecert-ca
  - Orderer1 : grpcs://org0-orderer1
  - Orderer2 : grpcs://org0-orderer2
  - Orderer3 : grpcs://org0-orderer3


- Org1 (org1.example.com):
  - TLS Certificate Authority : https://org1-tls-ca
  - ECert Certificate Authority : https://org1-ecert-ca
  - Peer Node 1 : grpcs://org1-peer1
  - Peer Node 2 : grpcs://org1-peer2


- Org2 (org2.example.com):
  - TLS Certificate Authority : https://org2-tls-ca
  - ECert Certificate Authority : https://org2-ecert-ca
  - Peer Node 1 : grpcs://org2-peer1
  - Peer Node 2 : grpcs://org2-peer2



### Next : [Working With Channels](CHANNELS.md)

