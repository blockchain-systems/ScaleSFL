npx caliper launch manager \
    --caliper-workspace . \
    --caliper-benchconfig benchmarks/config.yaml \
    --caliper-networkconfig networks/fabric-config.yaml \
    --caliper-flow-only-test \
    --caliper-fabric-gateway-enabled

mv report.html reports/report.html