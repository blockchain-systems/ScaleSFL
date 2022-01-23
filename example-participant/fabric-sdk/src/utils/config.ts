import fs from "fs/promises";
import { OrganizationInfo } from "src/interfaces/organization";

export const getConnectionProfile = async (
    connectionProfileFileName: string
): Promise<Record<string, any>> => {
    const connectionProfileJson = (await fs.readFile(connectionProfileFileName)).toString();
    const connectionProfile = JSON.parse(connectionProfileJson);

    return connectionProfile;
};

export const getOrgInfo = (shardId: number): OrganizationInfo => ({
    connectionProfile: `../../test-network/organizations/peerOrganizations/org${
        shardId + 1
    }.example.com/connection-org${shardId + 1}.json`,
    hostname: `ca.org${shardId + 1}.example.com`,
    msp_org: `Org${shardId + 1}MSP`
});
