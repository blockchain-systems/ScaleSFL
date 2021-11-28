import { Context, Contract, Info, Returns, Transaction } from "fabric-contract-api";
import stringify from "json-stringify-deterministic";
import sortKeysRecursive from "sort-keys-recursive";
import { Shard } from "./shard";

@Info({ title: "ShardCatalyst", description: "Smart contract coordinating models across shards" })
export class ShardCatalystContract extends Contract {
    // initialize ledger with set of shards (representing channels)
    @Transaction()
    public async InitLedger(ctx: Context): Promise<void> {
        const shards: Shard[] = [
            {
                ID: "1",
                Channel: "CIFAR1",
                MinPeers: 0,
                PinnedHash: ""
            },
            {
                ID: "2",
                Channel: "CIFAR2",
                MinPeers: 0,
                PinnedHash: ""
            }
        ];

        for (const shard of shards) {
            shard.docType = "shard";
            await ctx.stub.putState(shard.ID, Buffer.from(stringify(sortKeysRecursive(shard))));
            console.info(`Shard ${shard.ID} initialized`);
        }
    }

    // CreateShard issues a new shard to the world state with given details.
    @Transaction()
    public async CreateShard(
        ctx: Context,
        id: string,
        channel: string,
        minPeers: number,
        pinnedHash: string
    ): Promise<void> {
        const exists = await this.ShardExists(ctx, id);
        if (exists) {
            throw new Error(`The shard ${id} already exists`);
        }

        const shard: Shard = {
            docType: "shard",
            ID: id,
            Channel: channel,
            MinPeers: minPeers,
            PinnedHash: pinnedHash
        };
        await ctx.stub.putState(id, Buffer.from(stringify(sortKeysRecursive(shard))));
    }

    // ReadShard returns the shard stored in the world state with given id.
    @Transaction(false)
    @Returns("string")
    public async ReadShard(ctx: Context, id: string): Promise<string> {
        const shardJSON = await ctx.stub.getState(id); // get the shard from chaincode state
        if (!shardJSON || shardJSON.length === 0) {
            throw new Error(`The shard ${id} does not exist`);
        }
        return shardJSON.toString();
    }

    // UpdateShard updates an existing shard in the world state with provided parameters.
    @Transaction()
    public async UpdateShard(
        ctx: Context,
        id: string,
        channel: string,
        minPeers: number,
        pinnedHash: string
    ): Promise<void> {
        const exists = await this.ShardExists(ctx, id);
        if (!exists) {
            throw new Error(`The shard ${id} does not exist`);
        }

        // overwriting original shard with new shard
        const updatedShard: Shard = {
            docType: "shard",
            ID: id,
            Channel: channel,
            MinPeers: minPeers,
            PinnedHash: pinnedHash
        };
        return ctx.stub.putState(id, Buffer.from(stringify(sortKeysRecursive(updatedShard))));
    }

    // DeleteShard deletes an given shard from the world state.
    @Transaction()
    public async DeleteShard(ctx: Context, id: string): Promise<void> {
        const exists = await this.ShardExists(ctx, id);
        if (!exists) {
            throw new Error(`The shard ${id} does not exist`);
        }
        return ctx.stub.deleteState(id);
    }

    // ShardExists returns true when shard with given ID exists in world state.
    @Transaction(false)
    @Returns("boolean")
    public async ShardExists(ctx: Context, id: string): Promise<boolean> {
        const shardJSON = await ctx.stub.getState(id);
        return shardJSON && shardJSON.length > 0;
    }

    // GetAllShards returns all shards found in the world state.
    @Transaction(false)
    @Returns("string")
    public async GetAllShards(ctx: Context): Promise<string> {
        const allResults = [];
        // range query with empty string for startKey and endKey does an open-ended query of all shards in the chaincode namespace.
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
