import argparse
import glob
import json
import stanza
import tqdm

from datetime import datetime
from tika import parser
import openreview_lib as orl

arg_parser = argparse.ArgumentParser(description="")
arg_parser.add_argument("-d", "--directory", default="", type=str, help="")
arg_parser.add_argument("-c", "--conference", default="", type=str, help="")

STANZA_PIPELINE = stanza.Pipeline(
    "en",
    processors="tokenize",
)
VERSIONS = [
    orl.EventType.PRE_REBUTTAL_REVISION,
    orl.EventType.REBUTTAL_REVISION,
    orl.EventType.FINAL_REVISION,
]
PLACEHOLDER = "$$$$$$$$"


def extract_text(pdf_path):
  raw = parser.from_file(pdf_path)
  if raw["content"] is None:
    return ""
  return (raw["content"].replace("-\n",
                                 "").replace("\n\n", PLACEHOLDER).replace(
                                     "\n", " ").replace(PLACEHOLDER, "\n\n"))


def tokenize(text):
  doc = STANZA_PIPELINE(text)
  tokens = []
  for sentence in doc.sentences:
    tokens.append([token.to_dict()[0]["text"] for token in sentence.tokens])
  return tokens


def main():

  args = arg_parser.parse_args()

  for directory_name in tqdm.tqdm(
      glob.glob(f"{args.directory}/{args.conference}/*")):
    forum = directory_name.split("/")[-1]
    print(f"{forum}\t", end="")
    found_versions = []
    for version in VERSIONS:
      if os.path.exists(f"{directory_name}/{version}.pdf"):
        found_versions.append(version)
    texts = {
        version: extract_text(f"{directory_name}/{version}.pdf")
        for version in found_versions
    }
    if set(texts.values()) == set([""]):
      print("failed")
    else:
      tokens = {version: tokenize(texts[version]) for version in found_versions}
      with open(f"{directory_name}/tokens.json", "w") as g:
        print("tokenized")
        json.dump(tokens, g)


if __name__ == "__main__":
  main()
