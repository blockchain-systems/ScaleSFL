import bodyParser from "body-parser";
import express from "express";
import morgan from "morgan";
import { Client } from "./client";
import {
    CONNECTION_PROFILE_ORG1,
    MSP_ORG_1,
    ORG1_HOSTNAME,
    USER_AFFILIATION,
    USER_ID
} from "./constants";
import { ChaincodeTransaction } from "./interfaces/transaction";
import { buildCAClient } from "./utils/ca";
import { getConnectionProfile } from "./utils/config";
import { createWallet, enrollAdmin, registerAndEnrollUser } from "./utils/wallet";

const expressPort = process.env.PORT || 5000;

const main = async () => {
    const app = express();

    // middleware
    app.enable("trust proxy");
    app.use(morgan("tiny"));
    app.use(bodyParser.json());

    // Express handlers
    app.get("/", (_, res) => {
        res.send("Hello World!");
    });

    app.post("/transaction/query", async (req, res) => {
        const txReq = req.body as ChaincodeTransaction;
        const response = await client
            .network(txReq.channel)
            .contract(txReq.contract)
            .submitTransaction(txReq.contractFunction, txReq.args)
            .catch(err => {
                res.status(400), console.error(err);
            });
        res.send(response);
    });

    app.post("/transaction/invoke", async (req, res) => {
        const txReq = req.body as ChaincodeTransaction;
        const response = await client
            .network(txReq.channel)
            .contract(txReq.contract)
            .submitTransaction(txReq.contractFunction, txReq.args)
            .catch(err => {
                res.status(400), console.error(err);
            });
        res.send(response);
    });

    // System handlers
    process.on("exit", () => {
        client.disconnect();
    });

    // Prepare Fabric
    const client = new Client();
    const connectionProfile = await getConnectionProfile(CONNECTION_PROFILE_ORG1);
    const caClient = buildCAClient(connectionProfile, ORG1_HOSTNAME);
    const wallet = await createWallet();
    await enrollAdmin(caClient, wallet, MSP_ORG_1);
    await registerAndEnrollUser(caClient, wallet, MSP_ORG_1, USER_ID, USER_AFFILIATION);
    client.connect(connectionProfile, {
        wallet,
        identity: USER_ID,
        discovery: { enabled: true }
    });

    // Start server
    app.listen(expressPort, () => {
        console.log(`Starting Fabric SDK Client at http://localhost:${expressPort}`);
    });
};

main();
