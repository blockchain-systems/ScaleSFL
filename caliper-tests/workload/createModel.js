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
                this.txIndex,
                crypto.randomBytes(256).toString("hex"),
                "me",
                Math.random() * 100
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
