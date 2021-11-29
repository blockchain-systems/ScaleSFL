import { Object, Property } from "fabric-contract-api";

type ShardTypes = "shard";

@Object()
export class Shard {
    @Property()
    public docType?: ShardTypes = "shard";

    @Property()
    public ID!: string;

    @Property()
    public Channel!: string;

    // this can be found using the discovery CLI
    @Property()
    public MinPeers!: number;

    @Property()
    public PinnedHash!: string;
}
