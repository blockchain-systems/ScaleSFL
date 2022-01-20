"use strict";

const { WorkloadModuleBase } = require("@hyperledger/caliper-core");
const crypto = require("crypto");

const TEST_MODEL_HASH = "";
const TEST_CLIENT_SERVER = "http://192.168.1.170";
const TEST_CLIENT_PORT_START = 3000;

/**
 * Workload module for the benchmark round.
 */
class CreateModelsWorkload extends WorkloadModuleBase {
    constructor() {
        super();
        this.txIndex = 0;
    }

    /**
     * Assemble TXs for the round.
     * @return {Promise<TxStatus[]>}
     */
    async submitTransaction() {
        this.txIndex++;
        const modelHash =
            TEST_MODEL_HASH ||
            crypto.createHash("sha256").update(crypto.randomBytes(20)).digest("hex");
        // const shardId = Math.floor(Math.random() * this.roundArguments.contractIds.length);
        const contractId =
            this.roundArguments.contractIds[this.txIndex % this.roundArguments.contractIds.length];
        const shardId = parseInt(contractId[contractId.length - 1]);

        let args = {
            contractId: contractId,
            contractFunction: "CreateModel",
            // invokerIdentity: `User1@org${shardId + 1}.example.com`,
            invokerMspId: `Org${shardId + 1}MSP`,
            contractArguments: [
                `model_${modelHash}`, // ID
                modelHash, // Hash
                `worker${this.workerIndex}`, // Owner
                `${TEST_CLIENT_SERVER}:${TEST_CLIENT_PORT_START + shardId}`, // Server
                1, // Round
                50 + Math.random() * 50 // EvaluationAccuracy
            ],
            readOnly: false,
            timeout: 60
        };

        await this.sutAdapter.sendRequests(args);
    }
}

/**
 * Create a new instance of the workload module.
 * @return {WorkloadModuleInterface}
 */
function createWorkloadModule() {
    return new CreateModelsWorkload();
}

module.exports.createWorkloadModule = createWorkloadModule;
