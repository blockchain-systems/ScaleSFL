export interface ChaincodeTransaction {
    channel: string;
    contract: string;
    contractFunction: string;
    args: any[];
}
