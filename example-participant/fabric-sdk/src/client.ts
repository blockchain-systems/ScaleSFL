import { Contract, Gateway, GatewayOptions, Network } from "fabric-network";

export class Client {
    private gatewayOptions: GatewayOptions | undefined;
    private gateway: Gateway | undefined;

    private networkName: string | undefined;
    private lastNetworkName: string | undefined;
    private _network: Network | undefined;

    private chaincodeId: string | undefined;
    private lastChaincodeId: string | undefined;
    private _contract: Contract | undefined;

    public constructor() {}

    public async connect(
        connectionProfile: Record<string, unknown>,
        gatewayOptions: GatewayOptions
    ) {
        if (!this.gateway) this.gateway = new Gateway();
        this.gatewayOptions = gatewayOptions;

        await this.gateway?.connect(connectionProfile, this.gatewayOptions);

        return this;
    }

    public async getNetwork(): Promise<Network | undefined> {
        if (!this.networkName) return;

        this._network =
            this.lastNetworkName === this.networkName
                ? this._network
                : await this.gateway?.getNetwork(this.networkName);
        this.lastNetworkName = this.networkName;

        return this._network;
    }

    public async getContract(): Promise<Contract | undefined> {
        if (!this.networkName || !this.chaincodeId) return;

        const network = await this.getNetwork();
        this._contract =
            this.lastChaincodeId === this.chaincodeId
                ? this._contract
                : network?.getContract(this.chaincodeId);
        this.lastChaincodeId = this.chaincodeId;

        return this._contract;
    }

    public async submitTransaction(name: string, args: any[]): Promise<Buffer | undefined> {
        const contract = await this.getContract();
        return await contract?.submitTransaction(name, ...args);
    }

    public async evaluateTransaction(name: string, args: any[]): Promise<Buffer | undefined> {
        const contract = await this.getContract();
        return await contract?.evaluateTransaction(name, ...args);
    }

    public network(networkName: string): Client {
        this.networkName = networkName;

        return this;
    }

    public contract(chaincodeId: string): Client {
        this.chaincodeId = chaincodeId;

        return this;
    }

    public disconnect() {
        if (this.gateway) this.gateway.disconnect();
    }
}
