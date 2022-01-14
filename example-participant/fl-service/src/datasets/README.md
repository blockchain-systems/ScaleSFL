# Datasets

We use several benchmarks to evaluate performance. For non-IID data we'll use the Leaf benchmark as described below

## Leaf Benchmark

We use the Leaf dataset scripts found on [Github](https://github.com/TalwalkarLab/leaf), with the commands run below

### FEMNIST

To download the data use

```sh
./preprocess.sh -s niid --sf 0.1 -k 0 -t sample -tf 0.7 --smplseed 42 --spltseed 42
```

This will provide 368 non-IID clients, with a train split of 0.7

If you need to rerun the above command with different parameters first remove the following subfolders

```sh
rm -rf data/rem_user_data data/sampled_data data/test data/train
```
