import collections
import glob
import json
import sys
import re


class DiffType(object):
  ADDITION = "addition"
  REMOVAL = "removal"
  MODIFICATION = "modification"
  REPLACEMENT = "replacement"


Addition = collections.namedtuple("Addition", "location new")
Removal = collections.namedtuple("Removal", "location old")
Replacement = collections.namedtuple("Replacement", "location old new")
Diff = collections.namedtuple("Diff", "location old new", defaults=(None, None,
  None))

RE_MAP = {
    DiffType.REPLACEMENT: re.compile(
            r"Differences found on page ([0-9]+) \- The text '(.*)' was replaced by '(.*)'"
    ),
    DiffType.REMOVAL: re.compile(
            r"Differences found on page ([0-9]+) \- The text '(.*)' was removed"
    ),
    DiffType.ADDITION: re.compile(
            r"Differences found on page ([0-9]+) \- The text '(.*)' was added"),
}


def main():
  diffs = []
  non_diffs = []
  for filename in glob.glob(f'{sys.argv[1]}/*.txt'):
    with open(filename, "r") as f:
      diff_count = 0
      for line in f:
        if "Differences" not in line:
          continue
        flag = False
        for diff_type, diff_re in RE_MAP.items():
          match_obj = re.match(diff_re, line.split(":", 3)[3].strip())
          if match_obj is not None:
            if diff_type == DiffType.ADDITION:
              location, old = match_obj.groups()
              diff_obj = Diff(location=location, old=old)
            elif diff_type == DiffType.REMOVAL:
              location, new = match_obj.groups()
              diff_obj = Diff(location=location, new=new)
            else:
              location, old, new = match_obj.groups()
              diff_obj = Diff(location=location, old=old, new=new)
            diffs.append(diff_obj)
            flag = True
        if not flag:
          print(line)
          assert (("modi" in line and "Font" in line) or "The line" in line or
                  "The image" in line or "The curve" in line or
                  "The element" in line or "has wrong size" in line)
          non_diffs.append(line)

    with open(filename.replace('.txt', ".jsonl"), 'w') as f:
      for i in diffs:
        f.write(json.dumps(i._asdict()) + "\n")


if __name__ == "__main__":
  main()
