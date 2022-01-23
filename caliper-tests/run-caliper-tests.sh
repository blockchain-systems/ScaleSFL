run_benchmark() {
    benchmark_name=$1
    
    # Run benchmark
    # Check https://hyperledger.github.io/caliper/vNext/runtime-config/ for more configuration settings
    npx caliper launch manager \
        --caliper-workspace . \
        --caliper-benchconfig benchmarks/${benchmark_name}.yaml \
        --caliper-networkconfig networks/fabric-config.yaml \
        --caliper-progress-reporting-interval 2000 \
        --caliper-flow-only-test \
        --caliper-worker-pollinterval 500 \
        --caliper-fabric-gateway-enabled
}

run_benchmark model-creation
mv report.html reports/report.html

# Test workers 
for i in {1..10..1}; do 
    sed -i -r "s/number: [[:digit:]]+/number: $i/" benchmarks/model-creation.yaml
    run_benchmark model-creation
    mv report.html reports/report-workers-${i}.html
done
# Set back to 4 workers
sed -i -r "s/number: [[:digit:]]+/number: 4/" benchmarks/model-creation.yaml

# Test TxCount
for i in {10..2000..10}; do 
    sed -i -r "s/\&txnum [[:digit:]]+/\&txnum $i/" benchmarks/model-creation.yaml
    run_benchmark model-creation
    mv report.html reports/report-txcnt-${i}.html
done
# Set back to 200 txs
sed -i -r "s/\&txnum [[:digit:]]+/\&txnum 200/" benchmarks/model-creation.yaml

# Test TPS
for i in {3..30..3}; do 
    sed -i -r "s/tps: [[:digit:]]+/tps: $i/g" benchmarks/model-creation.yaml
    run_benchmark model-creation
    mv report.html reports/report-tps-${i}.html
done

