import FabricCAServices from "fabric-ca-client";

export const buildCAClient = (ccp: Record<string, any>, caHostName: string): FabricCAServices => {
    const caInfo = ccp.certificateAuthorities[caHostName];
    const caTLSCACerts = caInfo.tlsCACerts.pem;
    const caClient = new FabricCAServices(
        caInfo.url,
        { trustedRoots: caTLSCACerts, verify: false },
        caInfo.caName
    );

    return caClient;
};
