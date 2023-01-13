import argparse
import collections
import glob
import json
import myers
import os
import re
import stanza
import tqdm

from datetime import datetime
from tika import parser
import openreview_lib as orl

arg_parser = argparse.ArgumentParser(description="")
arg_parser.add_argument("-d", "--directory", default="", type=str, help="")
arg_parser.add_argument("-c", "--conference", default="", type=str, help="")

Diff = collections.namedtuple("Diff",
                              "location old new",
                              defaults=(None, None, None))

STANZA_PIPELINE = stanza.Pipeline(
    "en",
    processors="tokenize",
)
VERSIONS = [orl.EventType.PRE_REBUTTAL_REVISION, orl.EventType.FINAL_REVISION]
FIRST, LAST = VERSIONS
PLACEHOLDER = "$$$$$$$$"

def extract_text(pdf_path):
  raw = parser.from_file(pdf_path)
  return (raw["content"].replace("-\n",
                                 "").replace("\n\n", PLACEHOLDER).replace(
                                     "\n", " ").replace(PLACEHOLDER, "\n\n"))



def tokenize(text):
  doc = STANZA_PIPELINE(text)
  tokens = []
  for sentence in doc.sentences:
    tokens.append([token.to_dict()[0]["text"] for token in sentence.tokens])
  return tokens


def check_reconstruction(first_tokens, last_tokens, diff_map):

  constructed_final_tokens = []

  i = 0
  while i < len(first_tokens):
    if i not in diff_map:
      constructed_final_tokens.append(first_tokens[i])
      i += 1
    else:
      diff = diff_map[i]
      if diff.old is None:
        constructed_final_tokens.append(first_tokens[i])
        i += 1
      else:
        i += len(diff.old)
      if diff.new is not None:
        constructed_final_tokens += list(diff.new)

  return constructed_final_tokens == last_tokens


def make_diffs(first_tokens_sentencized, last_tokens_sentencized, check=False):
  first_tokens = sum(first_tokens_sentencized, [])
  last_tokens = sum(last_tokens_sentencized, [])
  if first_tokens == last_tokens:
    return

  print(f"Starting diff {datetime.now().strftime('%H:%M:%S')}")
  myers_diff = myers.diff(first_tokens, last_tokens)
  first_file_indices = []
  current_first_file_index = -1
  for action, token in myers_diff:
    if action in "kr":
      current_first_file_index += 1
    first_file_indices.append(current_first_file_index)

  diff_map = {}
  action_string = "".join(x[0] for x in myers_diff)
  for match in re.finditer("[ir]+", action_string):
    assert re.match("^r*i*$|^i*r*$", match.group()) is not None
    tokens_added = []
    tokens_deleted = []
    start, end = match.start(), match.end()
    for action, token in myers_diff[start:end]:
      if action == "i":
        tokens_added.append(token)
      else:
        tokens_deleted.append(token)
    location = first_file_indices[start]
    diff_map[location] = Diff(
        location=location,
        old=(tuple(tokens_deleted) if tokens_deleted else None),
        new=(tuple(tokens_added) if tokens_added else None),
    )

  if check:
    assert check_reconstruction(first_tokens, last_tokens, diff_map)

  return {
      "tokens": {
          FIRST: first_tokens_sentencized,
          LAST: last_tokens_sentencized
      },
      "diffs":
          sorted([d._asdict() for d in diff_map.values()],
                 key=lambda x: x["location"]),
          }


def main():

  args = arg_parser.parse_args()

  for directory_name in tqdm.tqdm(
      glob.glob(f"{args.directory}/{args.conference}/*")):
    forum = directory_name.split("/")[-1]
    version_missing = False
    for version in VERSIONS:
      if not os.path.exists(f'{directory_name}/{version}.pdf'):
        print(f"Skipping {forum}, no {version}")
        version_missing = True
    if version_missing:
      continue
    texts = {
        version: extract_text(f"{directory_name}/{version}.pdf")
        for version in VERSIONS
    }
    tokens = {
        version: tokenize(texts[version]) for version in VERSIONS
        }
    with open(f"{directory_name}/diffs.json", "w") as g:
      json.dump(
          make_diffs(
            tokens[FIRST],
            tokens[LAST]), g)


if __name__ == "__main__":
  main()
