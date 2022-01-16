def round_robin(client_id: int, num_shards: int) -> int:
    num_shards = max(num_shards, 1)

    return client_id % num_shards
