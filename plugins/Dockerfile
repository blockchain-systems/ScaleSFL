FROM golang:1.16.7-alpine3.14

RUN apk add --no-cache \
	bash \
	gcc \
	git \
	make \
	musl-dev

ADD ./modelEndorsement $GOPATH/src/github.com/hyperledger/fabric
WORKDIR $GOPATH/src/github.com/hyperledger/fabric

RUN go build -buildmode=plugin -o escc.so plugin.go