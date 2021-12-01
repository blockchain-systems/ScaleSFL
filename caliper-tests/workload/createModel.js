"use strict";

const { WorkloadModuleBase } = require("@hyperledger/caliper-core");
const crypto = require("crypto");

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

        let args = {
            contractId: this.roundArguments.contractId,
            contractFunction: "CreateModel",
            invokerIdentity: "User1",
            contractArguments: [
                `model_${this.workerIndex}_${this.txIndex}`, // ID
                crypto.randomBytes(256).toString("hex"), // Hash
                `worker${this.workerIndex}`, // Owner
                "http://192.168.1.170:3000", // Server
                1, // Round
                Math.random() * 100 // EvaluationAccuracy
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
