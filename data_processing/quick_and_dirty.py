import openreview
import openreview_lib as orl
import os
import tqdm

GUEST_CLIENT = openreview.Client(baseurl="https://api.openreview.net")

def get_review_boundaries(forum_note_id):
  """Get earliest and latest review creation (modification?)"""
  creation_dates = []
  review_found = False
  for note in GUEST_CLIENT.get_notes(forum=forum_note_id):
    if 'review' in note.content or 'main_review' in note.content:
      review_found = True
      creation_dates.append(note.tcdate)
  if not review_found:
    return None, None
  assert review_found
  return min(creation_dates), max(creation_dates)

def get_decision(forum_note_id):
  """Get decision from metareview"""
  decision_found = False
  for note in GUEST_CLIENT.get_notes(forum=forum_note_id):
    for key in ['decision', 'recommendation']:
      if key in note.content:
        return note.content[key]
  assert False


OUTPUT_DIR = "qad_outputs"

def main():

  for conference, invitation in orl.INVITATION_MAP.items():
    forum_notes = list(
      openreview.tools.iterget_notes(
          GUEST_CLIENT, invitation=orl.INVITATION_MAP[conference]))
    conference_dir = f'{OUTPUT_DIR}/{conference}'
    
    for forum_note in tqdm.tqdm(forum_notes):
      forum_dir = f'{conference_dir}/{forum_note.id}'
      os.makedirs(forum_dir, exist_ok=True)
      decision = get_decision(forum_note.id)
      earliest_date, _ = get_review_boundaries(forum_note.id)
      if earliest_date is None:
        print(conference, decision[:5], "No reviews")
        continue
      revisions = sorted(GUEST_CLIENT.get_all_references(referent=forum_note.id,
        original=True), key=lambda x:x.tmdate)
      earliest_revision = None
      for i, revision in enumerate(revisions):
        if revision.tmdate > earliest_date:
          earliest_revision = revisions[i-1]
          break
      if earliest_revision is not None:
        try:  # try to get the PDF for this submission or revision
          pdf_binary = GUEST_CLIENT.get_pdf(earliest_revision.id, is_reference=True)
          with open(f'{forum_dir}/first.pdf', 'wb') as f:
            f.write(pdf_binary)
          pdf_binary = GUEST_CLIENT.get_pdf(revisions[-1].id, is_reference=True)
          with open(f'{forum_dir}/last.pdf', 'wb') as f:
            f.write(pdf_binary)
          print(conference, decision[:5], earliest_revision.id,
              revisions[-1].id, "Success")
        except openreview.OpenReviewException as e:
          print(conference, decision[:5], earliest_revision.id,
              revisions[-1].id, "Failure", orl.PDF_ERROR_STATUS_LOOKUP[e.args[0]["name"]])

      else:
        print(conference, decision[:5], "No revisions")

      


if __name__ == "__main__":
  main()
