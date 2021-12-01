import fs from "fs/promises";

export const getConnectionProfile = async (
    connectionProfileFileName: string
): Promise<Record<string, any>> => {
    const connectionProfileJson = (await fs.readFile(connectionProfileFileName)).toString();
    const connectionProfile = JSON.parse(connectionProfileJson);

    return connectionProfile;
};
