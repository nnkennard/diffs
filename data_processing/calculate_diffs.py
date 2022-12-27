import collections
import glob
import itertools
import subprocess
import sys
import tqdm


def main():

  pdf_lists = collections.defaultdict(list)

  for filename in glob.glob(f"{sys.argv[1]}/*.pdf"):
    orig_filename, version_str = (filename.split("/")[-1].split(".")[0].rsplit(
        "__", 1))
    pdf_lists[orig_filename].append((int(version_str), filename))

  for orig_filename, versions in tqdm.tqdm(pdf_lists.items()):
    sorted_versions = list(sorted(versions))
    print(f"{len(versions)} versions")
    for i in range(len(versions) - 1):
      v_1_idx, v_1_path = sorted_versions[i]
      v_2_idx, v_2_path = sorted_versions[i + 1]
      output_file = f"diff_logs/{orig_filename}__{v_1_idx}_{v_2_idx}.txt"
      subprocess.run(
          ["bash", "compare_two_pdfs.sh", v_1_path, v_2_path, output_file])


if __name__ == "__main__":
  main()
