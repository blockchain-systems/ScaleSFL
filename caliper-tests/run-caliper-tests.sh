# Config
num_shards=8
reports_dir="reports"
benchmark_config="model-creation"

# Script Metrics
starttime=$(date +%s)

set_workers() {
    local benchmark_name=$1
    local workers=$2
    
    sed -i -r "s/number: [[:digit:]]+/number: $workers/" benchmarks/${benchmark_name}.yaml
}

set_tps() {
    local benchmark_name=$1
    local tps=$2

    sed -i -r "s/tps: [[:digit:]]+/tps: ${tps}/g" benchmarks/${benchmark_name}.yaml
}

set_txcnt() {
    local benchmark_name=$1
    local txcnt=$2
    
    sed -i -r "s/\&txnum [[:digit:]]+/\&txnum $txcnt/" benchmarks/${benchmark_name}.yaml
}

set_num_shards() {
    local benchmark_name=$1
    local shards=$2

    # Label
    sed -i -r "s/simulating [[:digit:]]+/simulating $shards/" benchmarks/${benchmark_name}.yaml

    # Contract Ids
    contractIds=$(seq -s " " -f "models%g" 0 $(($shards - 1)))
    sed -i -r "s/contractIds: \[.*\]/contractIds: \[${contractIds// /,}\]/" benchmarks/${benchmark_name}.yaml

    # Set tps
    set_tps $benchmark_name $(($shards * 3 + 3))
}   

run_benchmark() {
    local benchmark_name=$1
    local filename=$2

    : ${filename:="report"}

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

    # Move report to repots directory 
    mkdir -p "${reports_dir}/${benchmark_name}"
    mv report.html "${reports_dir}/${benchmark_name}/${filename}.html"
}

run_benchmark_shards() {
    local benchmark_name=$1
    local filename=$2

    : ${filename:="report"}

    for s in $(seq 1 $num_shards); do
        set_num_shards $benchmark_name $s
        run_benchmark $benchmark_name ${filename}_shards${s}
    done
}

# Initial config
set_txcnt $benchmark_config 50
set_workers $benchmark_config 2

run_benchmark_shards $benchmark_config

# Test workers 
for i in {1..10..1}; do 
    set_workers $benchmark_config $i
    run_benchmark_shards $benchmark_config report_workers${i}
done
# Set back to 2 workers
set_workers $benchmark_config 2

# Test TxCount
for i in {10..2000..10}; do 
    set_txcnt $benchmark_config $i
    run_benchmark_shards $benchmark_config report_txcnt${i}
done
# Set back to 200 txs
set_txcnt $benchmark_config 200

# Test TPS
for i in {3..30..3}; do 
    set_tps $benchmark_config $i
    run_benchmark_shards $benchmark_config report_tps${i}
done

echo "Total benchmark time: $(($(date +%s) - starttime))s"