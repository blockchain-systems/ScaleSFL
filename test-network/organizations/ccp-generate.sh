#!/bin/bash

function one_line_pem {
    echo "`awk 'NF {sub(/\\n/, ""); printf "%s\\\\\\\n",$0;}' $1`"
}

function json_ccp {
    local PP=$(one_line_pem $4)
    local CP=$(one_line_pem $5)
    sed -e "s/\${ORG}/$1/" \
        -e "s/\${P0PORT}/$2/" \
        -e "s/\${CAPORT}/$3/" \
        -e "s#\${PEERPEM}#$PP#" \
        -e "s#\${CAPEM}#$CP#" \
        organizations/ccp-template.json
}

function yaml_ccp {
    local PP=$(one_line_pem $4)
    local CP=$(one_line_pem $5)
    sed -e "s/\${ORG}/$1/" \
        -e "s/\${P0PORT}/$2/" \
        -e "s/\${CAPORT}/$3/" \
        -e "s#\${PEERPEM}#$PP#" \
        -e "s#\${CAPEM}#$CP#" \
        organizations/ccp-template.yaml | sed -e $'s/\\\\n/\\\n          /g'
}

ORG=1
P0PORT=7051
CAPORT=7054
PEERPEM=organizations/peerOrganizations/org1.example.com/tlsca/tlsca.org1.example.com-cert.pem
CAPEM=organizations/peerOrganizations/org1.example.com/ca/ca.org1.example.com-cert.pem

echo "$(json_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org1.example.com/connection-org1.json
echo "$(yaml_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org1.example.com/connection-org1.yaml

ORG=2
P0PORT=9051
CAPORT=8054
PEERPEM=organizations/peerOrganizations/org2.example.com/tlsca/tlsca.org2.example.com-cert.pem
CAPEM=organizations/peerOrganizations/org2.example.com/ca/ca.org2.example.com-cert.pem

echo "$(json_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org2.example.com/connection-org2.json
echo "$(yaml_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org2.example.com/connection-org2.yaml

ORG=3
P0PORT=11051
CAPORT=11054
PEERPEM=organizations/peerOrganizations/org3.example.com/tlsca/tlsca.org3.example.com-cert.pem
CAPEM=organizations/peerOrganizations/org3.example.com/ca/ca.org3.example.com-cert.pem

echo "$(json_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org3.example.com/connection-org3.json
echo "$(yaml_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org3.example.com/connection-org3.yaml

ORG=4
P0PORT=12051
CAPORT=12054
PEERPEM=organizations/peerOrganizations/org4.example.com/tlsca/tlsca.org4.example.com-cert.pem
CAPEM=organizations/peerOrganizations/org4.example.com/ca/ca.org4.example.com-cert.pem

echo "$(json_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org4.example.com/connection-org4.json
echo "$(yaml_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org4.example.com/connection-org4.yaml

ORG=5
P0PORT=13051
CAPORT=13054
PEERPEM=organizations/peerOrganizations/org5.example.com/tlsca/tlsca.org5.example.com-cert.pem
CAPEM=organizations/peerOrganizations/org5.example.com/ca/ca.org5.example.com-cert.pem

echo "$(json_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org5.example.com/connection-org5.json
echo "$(yaml_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org5.example.com/connection-org5.yaml

ORG=6
P0PORT=14051
CAPORT=14054
PEERPEM=organizations/peerOrganizations/org6.example.com/tlsca/tlsca.org6.example.com-cert.pem
CAPEM=organizations/peerOrganizations/org6.example.com/ca/ca.org6.example.com-cert.pem

echo "$(json_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org6.example.com/connection-org6.json
echo "$(yaml_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org6.example.com/connection-org6.yaml

ORG=7
P0PORT=15051
CAPORT=15054
PEERPEM=organizations/peerOrganizations/org7.example.com/tlsca/tlsca.org7.example.com-cert.pem
CAPEM=organizations/peerOrganizations/org7.example.com/ca/ca.org7.example.com-cert.pem

echo "$(json_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org7.example.com/connection-org7.json
echo "$(yaml_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org7.example.com/connection-org7.yaml

ORG=8
P0PORT=16051
CAPORT=16054
PEERPEM=organizations/peerOrganizations/org8.example.com/tlsca/tlsca.org8.example.com-cert.pem
CAPEM=organizations/peerOrganizations/org8.example.com/ca/ca.org8.example.com-cert.pem

echo "$(json_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org8.example.com/connection-org8.json
echo "$(yaml_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org8.example.com/connection-org8.yaml