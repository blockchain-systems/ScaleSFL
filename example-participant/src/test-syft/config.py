batch_size = 64
lr = 0.1  # learning rate

name = "mnist"
version = "1.0"

client_config = {
    "name": name,
    "version": version,
    "batch_size": batch_size,
    "lr": lr,
    "max_updates": 1,  # custom syft.js option that limits number of training loops per worker
}

server_config = {
    "min_workers": 2,
    "max_workers": 2,
    "pool_selection": "random",
    "do_not_reuse_workers_until_cycle": 6,
    "cycle_length": 28800,  # max cycle length in seconds
    "num_cycles": 30,  # max number of cycles
    "max_diffs": 1,  # number of diffs to collect before avg
    "minimum_upload_speed": 0,
    "minimum_download_speed": 0,
    "iterative_plan": True,  # tells PyGrid that avg plan is executed per diff
}
