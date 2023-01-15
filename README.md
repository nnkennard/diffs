# diffs
Installation
```
pip install openreview-py pytz tqdm myers stanza tika
```

Request CPUs on swarm:
```
srun --pty --partition=longq --cpus-per-task=7 -t 4-00:00 --mem=100GB /bin/bash
```

Build the dataset:
```
cd data_processing
python get_openreview_data.py -c iclr_2022 -o ICLR2022
python 01_extract_diffs.py -d ICLR2022 -c iclr_2022
```


