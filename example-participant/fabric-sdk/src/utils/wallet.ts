import FabricCAServices from "fabric-ca-client";
import { Wallet, Wallets } from "fabric-network";
import { ADMIN_USER_ID, ADMIN_USER_PASSWORD, WALLET_DIRECTORY_PATH } from "../constants";

export const createWallet = async (
    clientId: string,
    walletDirectoryPath: string = WALLET_DIRECTORY_PATH
) => {
    return await Wallets.newFileSystemWallet(`${walletDirectoryPath}/${clientId}`);
};

export const enrollAdmin = async (caClient: FabricCAServices, wallet: Wallet, orgMspId: string) => {
    try {
        const identity = await wallet.get(ADMIN_USER_ID);
        if (identity) {
            console.log("An identity for the admin user already exists in the wallet");
            return;
        }

        const enrollment = await caClient.enroll({
            enrollmentID: ADMIN_USER_ID,
            enrollmentSecret: ADMIN_USER_PASSWORD
        });
        const x509Identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes()
            },
            mspId: orgMspId,
            type: "X.509"
        };
        await wallet.put(ADMIN_USER_ID, x509Identity);
    } catch (error) {
        console.error(`Failed to enroll admin user : ${error}`);
    }
};

export const registerAndEnrollUser = async (
    caClient: FabricCAServices,
    wallet: Wallet,
    orgMspId: string,
    userId: string,
    affiliation: string
) => {
    try {
        const userIdentity = await wallet.get(userId);
        if (userIdentity) {
            console.log(`An identity for the user ${userId} already exists in the wallet`);
            return;
        }

        const adminIdentity = await wallet.get(ADMIN_USER_ID);
        if (!adminIdentity) {
            console.log("An identity for the admin user does not exist in the wallet");
            console.log("Enroll the admin user before retrying");
            return;
        }

        const provider = wallet.getProviderRegistry().getProvider(adminIdentity.type);
        const adminUser = await provider.getUserContext(adminIdentity, ADMIN_USER_ID);

        const secret = await caClient.register(
            {
                affiliation,
                enrollmentID: userId,
                role: "client"
            },
            adminUser
        );
        const enrollment = await caClient.enroll({
            enrollmentID: userId,
            enrollmentSecret: secret
        });
        const x509Identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes()
            },
            mspId: orgMspId,
            type: "X.509"
        };
        await wallet.put(userId, x509Identity);
    } catch (error) {
        console.error(`Failed to register user : ${error}`);
    }
};
