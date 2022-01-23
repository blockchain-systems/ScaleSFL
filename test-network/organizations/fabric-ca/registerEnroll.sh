#!/bin/bash

function createOrg() {
  ORG=$1
  CA_PO=$2
  
  infoln "Enrolling the CA admin"
  mkdir -p organizations/peerOrganizations/org${ORG}.example.com/

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org${ORG}.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:${CA_PO} --caname ca-org${ORG} --tls.certfiles "${PWD}/organizations/fabric-ca/org${ORG}/tls-cert.pem"
  { set +x; } 2>/dev/null

  echo "NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-${CA_PO}-ca-org${ORG}.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-${CA_PO}-ca-org${ORG}.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-${CA_PO}-ca-org${ORG}.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-${CA_PO}-ca-org${ORG}.pem
    OrganizationalUnitIdentifier: orderer" > "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/msp/config.yaml"

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org${ORG} --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles "${PWD}/organizations/fabric-ca/org${ORG}/tls-cert.pem"
  { set +x; } 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org${ORG} --id.name user1 --id.secret user1pw --id.type client --tls.certfiles "${PWD}/organizations/fabric-ca/org${ORG}/tls-cert.pem"
  { set +x; } 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org${ORG} --id.name org${ORG}admin --id.secret org${ORG}adminpw --id.type admin --tls.certfiles "${PWD}/organizations/fabric-ca/org${ORG}/tls-cert.pem"
  { set +x; } 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:${CA_PO} --caname ca-org${ORG} -M "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/msp" --csr.hosts peer0.org${ORG}.example.com --tls.certfiles "${PWD}/organizations/fabric-ca/org${ORG}/tls-cert.pem"
  { set +x; } 2>/dev/null

  cp "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/msp/config.yaml" "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/msp/config.yaml"

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:${CA_PO} --caname ca-org${ORG} -M "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/tls" --enrollment.profile tls --csr.hosts peer0.org${ORG}.example.com --csr.hosts localhost --tls.certfiles "${PWD}/organizations/fabric-ca/org${ORG}/tls-cert.pem"
  { set +x; } 2>/dev/null

  cp "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/tls/tlscacerts/"* "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/tls/ca.crt"
  cp "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/tls/signcerts/"* "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/tls/server.crt"
  cp "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/tls/keystore/"* "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/tls/server.key"

  mkdir -p "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/msp/tlscacerts"
  cp "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/tls/tlscacerts/"* "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/msp/tlscacerts/ca.crt"

  mkdir -p "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/tlsca"
  cp "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/tls/tlscacerts/"* "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/tlsca/tlsca.org${ORG}.example.com-cert.pem"

  mkdir -p "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/ca"
  cp "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/peers/peer0.org${ORG}.example.com/msp/cacerts/"* "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/ca/ca.org${ORG}.example.com-cert.pem"

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:${CA_PO} --caname ca-org${ORG} -M "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/users/User1@org${ORG}.example.com/msp" --tls.certfiles "${PWD}/organizations/fabric-ca/org${ORG}/tls-cert.pem"
  { set +x; } 2>/dev/null

  cp "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/msp/config.yaml" "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/users/User1@org${ORG}.example.com/msp/config.yaml"

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org${ORG}admin:org${ORG}adminpw@localhost:${CA_PO} --caname ca-org${ORG} -M "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/users/Admin@org${ORG}.example.com/msp" --tls.certfiles "${PWD}/organizations/fabric-ca/org${ORG}/tls-cert.pem"
  { set +x; } 2>/dev/null

  cp "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/msp/config.yaml" "${PWD}/organizations/peerOrganizations/org${ORG}.example.com/users/Admin@org${ORG}.example.com/msp/config.yaml"
}

function createOrg1() {
  createOrg 1 7054
}

function createOrg2() {
  createOrg 2 8054
}

function createOrg3() {
  createOrg 3 11054
}

function createOrg4() {
  createOrg 4 12054
}

function createOrg5() {
  createOrg 5 13054
}

function createOrg6() {
  createOrg 6 14054
}

function createOrg7() {
  createOrg 7 15054
}

function createOrg8() {
  createOrg 8 16054
}

function createOrderer() {
  infoln "Enrolling the CA admin"
  mkdir -p organizations/ordererOrganizations/example.com

  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/ordererOrganizations/example.com

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:9054 --caname ca-orderer --tls.certfiles "${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem"
  { set +x; } 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-9054-ca-orderer.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-9054-ca-orderer.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-9054-ca-orderer.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-9054-ca-orderer.pem
    OrganizationalUnitIdentifier: orderer' > "${PWD}/organizations/ordererOrganizations/example.com/msp/config.yaml"

  infoln "Registering orderer"
  set -x
  fabric-ca-client register --caname ca-orderer --id.name orderer --id.secret ordererpw --id.type orderer --tls.certfiles "${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem"
  { set +x; } 2>/dev/null

  infoln "Registering the orderer admin"
  set -x
  fabric-ca-client register --caname ca-orderer --id.name ordererAdmin --id.secret ordererAdminpw --id.type admin --tls.certfiles "${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem"
  { set +x; } 2>/dev/null

  infoln "Generating the orderer msp"
  set -x
  fabric-ca-client enroll -u https://orderer:ordererpw@localhost:9054 --caname ca-orderer -M "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp" --csr.hosts orderer.example.com --csr.hosts localhost --tls.certfiles "${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem"
  { set +x; } 2>/dev/null

  cp "${PWD}/organizations/ordererOrganizations/example.com/msp/config.yaml" "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/config.yaml"

  infoln "Generating the orderer-tls certificates"
  set -x
  fabric-ca-client enroll -u https://orderer:ordererpw@localhost:9054 --caname ca-orderer -M "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls" --enrollment.profile tls --csr.hosts orderer.example.com --csr.hosts localhost --tls.certfiles "${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem"
  { set +x; } 2>/dev/null

  cp "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/tlscacerts/"* "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt"
  cp "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/signcerts/"* "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/server.crt"
  cp "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/keystore/"* "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/server.key"

  mkdir -p "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts"
  cp "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/tlscacerts/"* "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"

  mkdir -p "${PWD}/organizations/ordererOrganizations/example.com/msp/tlscacerts"
  cp "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/tlscacerts/"* "${PWD}/organizations/ordererOrganizations/example.com/msp/tlscacerts/tlsca.example.com-cert.pem"

  infoln "Generating the admin msp"
  set -x
  fabric-ca-client enroll -u https://ordererAdmin:ordererAdminpw@localhost:9054 --caname ca-orderer -M "${PWD}/organizations/ordererOrganizations/example.com/users/Admin@example.com/msp" --tls.certfiles "${PWD}/organizations/fabric-ca/ordererOrg/tls-cert.pem"
  { set +x; } 2>/dev/null

  cp "${PWD}/organizations/ordererOrganizations/example.com/msp/config.yaml" "${PWD}/organizations/ordererOrganizations/example.com/users/Admin@example.com/msp/config.yaml"
}
