from datetime import datetime as dt
import time, pytz


CONFERENCE_TO_INVITATION = {
    f"iclr_{year}": f"ICLR.cc/{year}/Conference/-/Blind_Submission"
    for year in range(2018, 2023)
}


def dt_to_unix(my_datetime):
    try:
        # naive datetime object (no time zone info), consider it a utc datetime
        return pytz.utc.localize(my_datetime).timestamp() * 1000
    except:
        # the datetime object already has time zone info
        return my_datetime.timestamp() * 1000


"""
We create datetime objects from UTC times, which we manually compute using 
times found from websites or with Open Review support.
The datetime objects are then converted to Unix timestamps (ms).
  
When there are multiple times for an occasion and we couldn't tell 
which is the most precise, we do the following.
1. review_release is used to get the last pre-rebuttal paper revision. We use the
earliest candidate to avoid mistakenly retrieving a revision during rebuttal.
2. rebuttal_end is used to get the last rebuttal revision. We use the latest 
candidate to avoid missing a revision during rebuttal.
"""
# TODO
CONFERENCE_TO_TIMES = {
    "iclr_2018": {
        "review_release":   dt_to_unix(dt(0, 0, 0, 0, 0, 0)),
        "rebuttal_end":     dt_to_unix(dt(0, 0, 0, 0, 0, 0)),
    },
    "iclr_2019": {
        "review_release":   dt_to_unix(dt(0, 0, 0, 0, 0, 0)),
        "rebuttal_end":     dt_to_unix(dt(0, 0, 0, 0, 0, 0)),
    },
    "iclr_2020": {
        "review_release":   dt_to_unix(dt(0, 0, 0, 0, 0, 0)),
        "rebuttal_end":     dt_to_unix(dt(0, 0, 0, 0, 0, 0)),
    },
    "iclr_2021": {
        "review_release":   dt_to_unix(dt(0, 0, 0, 0, 0, 0)),
        "rebuttal_end":     dt_to_unix(dt(0, 0, 0, 0, 0, 0)),
    },
    "iclr_2022": {
        "review_release":   dt_to_unix(dt(2021, 11, 9, 0, 0, 0)),
        "rebuttal_end":     dt_to_unix(dt(2021, 11, 24, 0, 30, 0)),
    },
}
for conf in CONFERENCE_TO_TIMES:
    assert CONFERENCE_TO_TIMES[conf]["review_release"] < CONFERENCE_TO_TIMES[conf]["rebuttal_end"]
print(CONFERENCE_TO_DEADLINES)