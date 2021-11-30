import { Context, Contract, Info, Returns, Transaction } from "fabric-contract-api";
import stringify from "json-stringify-deterministic";
import sortKeysRecursive from "sort-keys-recursive";
import { Model } from "./model";

@Info({ title: "ModelLedger", description: "Smart contract storing the state of a model" })
export class ModelLedgerContract extends Contract {
    // initialize ledger with a default model
    @Transaction()
    public async InitLedger(ctx: Context): Promise<void> {
        const models: Model[] = [
            {
                ID: "model1",
                Hash: "",
                Owner: "me",
                Server: "http://192.168.1.170:3000",
                Round: 1,
                EvaluationAccuracy: 0
            }
        ];

        for (const model of models) {
            model.docType = "model";
            await ctx.stub.putState(model.ID, Buffer.from(stringify(sortKeysRecursive(model))));
            console.info(`Model ${model.ID} initialized`);
        }
    }

    // CreateModel issues a new model to the world state with given details.
    @Transaction()
    public async CreateModel(
        ctx: Context,
        id: string,
        hash: string,
        owner: string,
        server: string,
        round: number,
        accuracy: number
    ): Promise<void> {
        const exists = await this.ModelExists(ctx, id);
        if (exists) {
            throw new Error(`The model ${id} already exists`);
        }

        const model: Model = {
            docType: "model",
            ID: id,
            Hash: hash,
            Owner: owner,
            Server: server,
            Round: round,
            EvaluationAccuracy: accuracy
        };
        await ctx.stub.putState(id, Buffer.from(stringify(sortKeysRecursive(model))));
    }

    // ReadModel returns the model stored in the world state with given id.
    @Transaction(false)
    @Returns("string")
    public async ReadModel(ctx: Context, id: string): Promise<string> {
        const modelJSON = await ctx.stub.getState(id); // get the model from chaincode state
        if (!modelJSON || modelJSON.length === 0) {
            throw new Error(`The model ${id} does not exist`);
        }
        return modelJSON.toString();
    }

    // UpdateModel updates an existing model in the world state with provided parameters.
    @Transaction()
    public async UpdateModel(
        ctx: Context,
        id: string,
        hash: string,
        owner: string,
        server: string,
        round: number,
        accuracy: number
    ): Promise<void> {
        const exists = await this.ModelExists(ctx, id);
        if (!exists) {
            throw new Error(`The model ${id} does not exist`);
        }

        // overwriting original model with new model
        const updatedModel: Model = {
            docType: "model",
            ID: id,
            Hash: hash,
            Owner: owner,
            Server: server,
            Round: round,
            EvaluationAccuracy: accuracy
        };
        return ctx.stub.putState(id, Buffer.from(stringify(sortKeysRecursive(updatedModel))));
    }

    // DeleteModel deletes an given model from the world state.
    @Transaction()
    public async DeleteModel(ctx: Context, id: string): Promise<void> {
        const exists = await this.ModelExists(ctx, id);
        if (!exists) {
            throw new Error(`The model ${id} does not exist`);
        }
        return ctx.stub.deleteState(id);
    }

    // ModelExists returns true when model with given ID exists in world state.
    @Transaction(false)
    @Returns("boolean")
    public async ModelExists(ctx: Context, id: string): Promise<boolean> {
        const modelJSON = await ctx.stub.getState(id);
        return modelJSON && modelJSON.length > 0;
    }

    // GetAllModels returns all models found in the world state.
    @Transaction(false)
    @Returns("string")
    public async GetAllModels(ctx: Context): Promise<string> {
        const allResults = [];
        // range query with empty string for startKey and endKey does an open-ended query of all models in the chaincode namespace.
        const iterator = await ctx.stub.getStateByRange("", "");
        let result = await iterator.next();
        while (!result.done) {
            const strValue = Buffer.from(result.value.value.toString()).toString("utf8");
            let record;
            try {
                record = JSON.parse(strValue);
            } catch (err) {
                console.log(err);
                record = strValue;
            }
            allResults.push(record);
            result = await iterator.next();
        }
        return JSON.stringify(allResults);
    }
}
