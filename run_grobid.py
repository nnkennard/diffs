import glob
import os
import subprocess
import tqdm

def main():

  for dir_name in tqdm.tqdm(glob.glob('data/pdfs/iclr_2019/*')):
    forum_id = dir_name.split("/")[-1]
    xml_dir = f'data/xmls/iclr_2019/{forum_id}/'
    os.makedirs(xml_dir, exist_ok=True)

    if len(glob.glob(f'{dir_name}/*')) == 1:
      continue
    
    subprocess.run([
        "java",
        "-Xmx4G",
        "-jar",
        f"grobid-0.7.2/grobid-core/build/libs/grobid-core-0.7.2-onejar.jar",
        "-r",
        "-gH",
        f"grobid-0.7.2/grobid-home",
        "-dIn",
        dir_name,
        "-dOut",
        xml_dir,
        "-exe",
        "processFullText",
    ],
    
        #stdout=subprocess.DEVNULL,
        #stderr=subprocess.DEVNULL,
    )


if __name__ == "__main__":
  main()
