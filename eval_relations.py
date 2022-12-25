import pandas as pd
import json
import numpy as np
import datetime

df = pd.read_csv('events_iclr_2019.tsv', delimiter='\t')
df2 = pd.read_csv('events_iclr_2020.tsv', delimiter='\t')
main_df = pd.concat([df, df2])

forums = main_df['forum'].unique()
print(forums)
forum_events = {}
for forum in forums:
    forum_events[forum] = []
    results = main_df[main_df['reply_to'] == forum]
    for i in range(len(results)):
        entry = results['filepath'].iloc[i]
        forum_events[forum].append([results['initiator'].iloc[i], entry + " created", results['tcdate'].iloc[i]])
        forum_events[forum].append([results['initiator'].iloc[i], entry + " modified", results['tmdate'].iloc[i]])
    forum_events[forum] = sorted(forum_events[forum], key= lambda x: x[2])
    forum_events[forum] = np.array(forum_events[forum])
    print(forum_events[forum])
    raise NotImplementedError()
