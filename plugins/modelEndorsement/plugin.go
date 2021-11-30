package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"os"

	"github.com/golang/protobuf/proto"
	"github.com/hyperledger/fabric-protos-go/peer"
	endorsement "github.com/hyperledger/fabric/core/handlers/endorsement/api"
	identities "github.com/hyperledger/fabric/core/handlers/endorsement/api/identities"
	"github.com/hyperledger/fabric/core/ledger/kvledger/txmgmt/rwsetutil"
)

var FLASK_SERVER = os.Getenv("FLASK_SERVER")

// To build the plugin,
// run:
//    go build -buildmode=plugin -o escc.so plugin.go

// ModelEndorsementFactory returns an endorsement plugin factory which returns plugins
// that behave as the model endorsement system chaincode
type ModelEndorsementFactory struct{}

// New returns an endorsement plugin that behaves as the model endorsement system chaincode
func (*ModelEndorsementFactory) New() endorsement.Plugin {
	return &ModelEndorsement{}
}

// ModelEndorsement is an endorsement plugin that behaves as the model endorsement system chaincode
type ModelEndorsement struct {
	identities.SigningIdentityFetcher
}

// Endorse signs the given payload(ProposalResponsePayload bytes), and optionally mutates it.
// Returns:
// The Endorsement: A signature over the payload, and an identity that is used to verify the signature
// The payload that was given as input (could be modified within this function)
// Or error on failure
func (e *ModelEndorsement) Endorse(prpBytes []byte, sp *peer.SignedProposal) (*peer.Endorsement, []byte, error) {
	signer, err := e.SigningIdentityForRequest(sp)
	if err != nil {
		return nil, nil, fmt.Errorf("failed fetching signing identity: %v", err)
	}
	// serialize the signing identity
	identityBytes, err := signer.Serialize()
	if err != nil {
		return nil, nil, fmt.Errorf("could not serialize the signing identity: %v", err)
	}

	// sign the concatenation of the proposal response and the serialized endorser identity with this endorser's key
	signature, err := signer.Sign(append(prpBytes, identityBytes...))
	if err != nil {
		return nil, nil, fmt.Errorf("could not sign the proposal response payload: %v", err)
	}
	endorsement := &peer.Endorsement{Signature: signature, Endorser: identityBytes}

	// Get the ProposalResponsePayload
	prp := &peer.ProposalResponsePayload{}
	proto.Unmarshal(prpBytes, prp)

	chaincodeAction := &peer.ChaincodeAction{}
	proto.Unmarshal(prp.Extension, chaincodeAction)

	txRWSet := &rwsetutil.TxRwSet{}
	txRWSet.FromProtoBytes(chaincodeAction.Results)

	txRWSetJSON, err := json.Marshal(txRWSet)

	resp, err := http.Post(FLASK_SERVER, "application/json", bytes.NewBuffer(txRWSetJSON))
	if err != nil {
		return nil, nil, fmt.Errorf("Could not evaluate model: %v", err)
	}
	if resp.StatusCode != 200 {
		return nil, nil, fmt.Errorf("Could not evaluate model: %v", err)
	}

	return endorsement, prpBytes, nil
}

// Init injects dependencies into the instance of the Plugin
func (e *ModelEndorsement) Init(dependencies ...endorsement.Dependency) error {
	for _, dep := range dependencies {
		sIDFetcher, isSigningIdentityFetcher := dep.(identities.SigningIdentityFetcher)
		if !isSigningIdentityFetcher {
			continue
		}
		e.SigningIdentityFetcher = sIDFetcher
		return nil
	}
	return errors.New("could not find SigningIdentityFetcher in dependencies")
}

// NewPluginFactory is the function ran by the plugin infrastructure to create an endorsement plugin factory.
func NewPluginFactory() endorsement.PluginFactory {
	return &ModelEndorsementFactory{}
}

func main() {}
