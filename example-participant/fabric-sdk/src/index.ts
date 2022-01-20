import bodyParser from "body-parser";
import express from "express";
import morgan from "morgan";
import { Client } from "./client";
import { ORG_INFO, USER_AFFILIATION, USER_ID } from "./constants";
import { ChaincodeTransaction } from "./interfaces/transaction";
import { buildCAClient } from "./utils/ca";
import { getConnectionProfile } from "./utils/config";
import { createWallet, enrollAdmin, registerAndEnrollUser } from "./utils/wallet";

const expressPort = process.env.PORT || 5000;
const shardId = parseInt(process.env.SHARD_ID ?? "0");

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
    const connectionProfile = await getConnectionProfile(ORG_INFO[shardId].connectionProfile);
    const caClient = buildCAClient(connectionProfile, ORG_INFO[shardId].hostname);
    const wallet = await createWallet(expressPort.toString());
    await enrollAdmin(caClient, wallet, ORG_INFO[shardId].msp_org);
    await registerAndEnrollUser(
        caClient,
        wallet,
        ORG_INFO[shardId].msp_org,
        `${USER_ID}${expressPort}`,
        USER_AFFILIATION
    );
    client.connect(connectionProfile, {
        wallet,
        identity: `${USER_ID}${expressPort}`,
        discovery: { enabled: true }
    });

    // Start server
    app.listen(expressPort, () => {
        console.log(`Starting Fabric SDK Client at http://localhost:${expressPort}`);
    });
};

main();
