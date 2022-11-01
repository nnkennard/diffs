import argparse
import collections
import hashlib
import json
import openreview
import os
import pandas as pd
import tqdm

from datetime import datetime

parser = argparse.ArgumentParser(description="")
parser.add_argument("-o",
                    "--output_dir",
                    default="data/text/",
                    type=str,
                    help="")
parser.add_argument("-p",
                    "--pdf_output_dir",
                    default="data/pdfs/",
                    type=str,
                    help="")
parser.add_argument("-c",
                    "--conference",
                    default="iclr_2019",
                    type=str,
                    help="")
parser.add_argument("-f", "--offset", default=0, type=int, help="")
parser.add_argument("-d", "--debug", action="store_true", help="")

INVITATION_MAP = {
    f"iclr_{year}": f"ICLR.cc/{year}/Conference/-/Blind_Submission"
    for year in range(2018, 2023)
}

# ==== HELPERS


def make_path(directories, filename=None):
  directory = os.path.join(*directories)
  os.makedirs(directory, exist_ok=True)
  if filename is not None:
    return os.path.join(*directories, filename)


def order_references(references):
  return list(sorted(references, key=lambda x: x.tmdate))


def maybe_transform_date(timestamp):
  if timestamp is None:
    return None
  else:
    return datetime.fromtimestamp(int(timestamp /
                                      1000)).strftime("%m/%d/%Y, %H:%M:%S")


def get_initiator(note):
  return note.signatures[0].split("/")[-1]


class PDFStatus(object):
  AVAILABLE = "available"
  DUPLICATE = "duplicate"
  FORBIDDEN = "forbidden"
  NOT_FOUND = "not_found"
  NOT_APPLICABLE = "not_applicable"


class EventType(object):
  COMMENT = "comment"
  ARTIFACT = "artifact"


def make_metadata_dict(reference, original_id, file_path, reference_index, pdf_status,
                       event_type):
  return {
      "forum": reference.forum,
      "initiator": get_initiator(reference),
      "original": original_id,
      "identifier": reference.id,
      "tcdate": reference.tcdate,
      "tmdate": reference.tmdate,
      "reply_to": reference.replyto,
      "reference_index": reference_index,
      "pdf_status": pdf_status,
      "event_type": event_type,
      "filepath": file_path,
  }


ERROR_STATUS_LOOKUP = {
    "ForbiddenError": PDFStatus.FORBIDDEN,
    "NotFoundError": PDFStatus.NOT_FOUND,
}


def write_artifact(
    guest_client,
    conference,
    note_id,
    reference,
    reference_index,
    directories,
    checksum_map,
):
  pdf_path = make_path(directories, f"artifact_{note_id}_{reference_index}.pdf")
  is_reference = not reference.id == reference.forum
  try:  # try to get the PDF for this reference
    pdf_binary = guest_client.get_pdf(reference.id, is_reference=is_reference)
    this_checksum = hashlib.md5(pdf_binary).hexdigest()
    found = False
    for other_pdf_path, other_checksum in checksum_map.items():
      if other_checksum == this_checksum:
        pdf_path = other_pdf_path
        pdf_status = PDFStatus.DUPLICATE
        found = True
    if not found:
      checksum_map[pdf_path] = this_checksum
      with open(pdf_path, "wb") as file_handle:
        file_handle.write(pdf_binary)
      pdf_status = PDFStatus.AVAILABLE
  except openreview.OpenReviewException as e:
    error_name = e.args[0]["name"]
    pdf_status = ERROR_STATUS_LOOKUP[error_name]

  return checksum_map, make_metadata_dict(reference, reference.forum, pdf_path, reference_index,
                                          pdf_status, EventType.ARTIFACT)


def write_comment(conference, note_id, reference, reference_index, directories):
  json_path = make_path(directories,
                        f"comment_{note_id}_{reference_index}.json")
  is_reference = not reference.id == reference.forum
  with open(json_path, "w") as f:
    json.dump(reference.content, f)
  return make_metadata_dict(
      reference,
      note_id,
      json_path,
      reference_index,
      PDFStatus.NOT_APPLICABLE,
      EventType.COMMENT,
  )


def main():
  args = parser.parse_args()
  assert args.conference in INVITATION_MAP

  # Get all 'forum' notes for the conference, filter if necessary
  guest_client = openreview.Client(baseurl="https://api.openreview.net")
  forum_notes = list(
      openreview.tools.iterget_notes(
          guest_client, invitation=INVITATION_MAP[args.conference]))

  processed_count = 0
  for i in tqdm.tqdm(range(args.offset, len(forum_notes), 10)):
    forum_notes_subset = forum_notes[i:i + 10]
    page_number = str(int(i / 10)).zfill(4)
    events = []

    for forum_note in tqdm.tqdm(forum_notes_subset):
      pdf_path = [args.pdf_output_dir, args.conference, forum_note.id]
      make_path(pdf_path)
      text_path = [args.output_dir, args.conference, forum_note.id]
      make_path(text_path)

      # Get all PDf revisions of the main submission, avoiding duplicates
      checksum_map = {}
      references = order_references(
          guest_client.get_references(referent=forum_note.id, original=True))
      # We don't run this line above with original=False. This would give us
      # the revisions to the Blind Submission itself, rather than the original
      # submission note.
      for pdf_ref_i, pdf_ref in enumerate(references):
        checksum_map, event_row = write_artifact(
            guest_client,
            args.conference,
            forum_note.id,
            pdf_ref,
            pdf_ref_i,
            pdf_path,
            checksum_map,
        )
        events.append(event_row)

      # Get PDFs from comments
      for note in guest_client.get_notes(forum=forum_note.id):
        if note.id == forum_note.id:  # Already done above
          continue
        references = order_references(
            guest_client.get_references(referent=note.id, original=False))
        # We don't run this line with original=True. This is because this flag
        # does not make sense for comment notes.
        for ref_i, reference in enumerate(references):
          events.append(
              write_comment(args.conference, note.id, reference, ref_i,
                            text_path))

    pd.DataFrame.from_dict(events).to_csv(
        f"{args.output_dir}/{args.conference}/events_{page_number}.tsv",
        sep="\t")
    if args.debug:
      break


if __name__ == "__main__":
  main()
