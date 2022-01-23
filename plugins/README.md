# Custom Endorsement Plugins

This defines a custom plugin for our sharded consensus mechanism

Following the [pluggable endorsement](https://hyperledger-fabric.readthedocs.io/en/release-2.2/pluggable_endorsement_and_validation.html), we'll create a [go plugin](https://pkg.go.dev/plugin)

To build the plugin use:

```sh
go build -buildmode=plugin -o escc.so plugin.go
```

This will produce a `escc.so` (endorsement system chaincode) shared library file. We'll specify this in the `config/core.yaml` file, as well as making volume of it for our peers, in the `test-network/docker/docker-compose-test-net.yaml`

Note we'll have to compile this with the same version of go, GOPATH, etc.

To do this we can use the same golang container used to build the peer. Versions can be found in the fabric [Makefile](https://github.com/hyperledger/fabric/blob/main/Makefile)

```sh
docker build -t hyperledger-plugin .
```

And run the image with

```sh
docker run --rm -it hyperledger-plugin sh
cp $CONTAINER_ID:/go/src/bfl/plugins/modelEndorsement/escc.so escc.so
```

Note a sample `escc.so` file has been included in this project  
Note you'll need to specifiy a flask url in the docker `docker-compose-test-net.yaml` file (for endorsements)

---

Alternatively we could build a new fabric-peer image, in the root workspace

```sh
git clone https://github.com/hyperledger/fabric
```

Check the releases page for the [version](https://github.com/hyperledger/fabric/releases) (commit hash)

e.g. v2.3.3 (this project uses) is `99553020d27768103e6cae2947ed6e96a7a7d08d`

```sh
cd fabric
git reset --hard $COMMIT_HASH
```

Make any changes necessary to the Dockerfile located in the `images/peer` directory (a sample is `Dockerfile.peer`), then

```sh
cp ../ScaleSFL/plugins/modelEndorsement/plugin.go core/handlers/endorsement/plugin/plugin.go
```

```sh
rm -rf build/
make peer-docker
```

To retrieve the plugin `.so` file you can use

```sh
docker cp $CONTAINER_ID:/etc/hyperledger/fabric/plugin/escc.so escc.so
```
