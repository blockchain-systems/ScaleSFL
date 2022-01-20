import { OrganizationInfo } from "./interfaces/organization";

export const WALLET_DIRECTORY_PATH = "wallet";

// Org1
export const ORG_INFO: OrganizationInfo[] = [
    {
        connectionProfile:
            "../../test-network/organizations/peerOrganizations/org1.example.com/connection-org1.json",
        hostname: "ca.org1.example.com",
        msp_org: "Org1MSP"
    },
    {
        connectionProfile:
            "../../test-network/organizations/peerOrganizations/org2.example.com/connection-org2.json",
        hostname: "ca.org2.example.com",
        msp_org: "Org2MSP"
    },
    {
        connectionProfile:
            "../../test-network/organizations/peerOrganizations/org3.example.com/connection-org3.json",
        hostname: "ca.org3.example.com",
        msp_org: "Org3MSP"
    }
];

// Identity
export const ADMIN_USER_ID = "admin";
export const ADMIN_USER_PASSWORD = "adminpw";

export const USER_ID = "appUser";
export const USER_AFFILIATION = "org1.department1";
