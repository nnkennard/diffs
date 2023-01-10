import collections


EVENT_FIELDS = [
    # Identifiers
    "forum_id",
    "referent_id",
    "revision_index",   # 0 indicates the referent, 1 is the first actual revision
    "note_id",
    "reply_to",         # 'replyto' from OpenReview
    # Event creator info
    "initiator",        # from 'signatures' from OpenReview
    "initiator_type",   # one of the InitiatorType strings
    # Date info
    "creation_date",    # 'true creation date' from OpenReview
    "mod_date",         # 'true modification date' from OpenReview
    # Event type info
    "event_type",       # see below
    "reply_to_type",    # None for paper revisions; one of EventType strings for comments
    # File info
    "json_path",
    "pdf_status",
    "pdf_path",         # None for comments
    "pdf_checksum",     # None for comments
]
Event = collections.namedtuple("Event", EVENT_FIELDS)


# A unified set of initiator types shared by all venues
# We ignore events' initiated by public readers
class InitiatorType(object):
    CONFERENCE      = "conference"
    AUTHOR          = "author"
    REVIEWER        = "reviewer"
    METAREVIEWER    = "metareviewer"
    OTHER           = "other"

# TODO Map conference-specific initiator types to our unified set of initiator types
def get_initiator_and_type(signatures, conference):
    initiators = [s.split("/")[-1] for s in signatures]
    combined_initiators = "|".join(initiators)

    for initiator in initiators:
        if "Conference" in initiator:
            return combined_initiators, InitiatorType.CONFERENCE



# A unified set of event types shared by all venues
class EventType(object):
    # paper
    PRE_REBUTTAL_REVISION   = "pre-rebuttal_revision"
    REBUTTAL_REVISION       = "rebuttal_revision"
    FINAL_REVISION          = "final_revision"
    # comments
    REVIEW              = "review"  # Official_Review which may have multiple revisions
    METAREVIEW          = "metareview"
    COMMENT             = "comment" # all other comments, whose types can be inferred
                                    # from initiator_type and reply_to_type

REVISION_TO_INDEX = {
    EventType.PRE_REBUTTAL_REVISION:    1,
    EventType.REBUTTAL_REVISION:        2,
    EventType.FINAL_REVISION:           3,
}

# TODO Map conference-specific comment event types to our unified set of event types
# This function handles comment notes, but not paper revisions.
def get_comment_event_type(note, conference):
    if conference == "iclr_2022":
        if "review" in note.content:
            return EventType.REVIEW
        elif "Decision" in note.invitation:
            return EventType.METAREVIEW
        else: # "Official_Comment" in note.
            return EventType.COMMENT


class PDFStatus(object):
    # for paper revisions
    AVAILABLE       = "available"
    DUPLICATE       = "duplicate"
    FORBIDDEN       = "forbidden"
    NOT_FOUND       = "not_found"
    # for comments
    NOT_APPLICABLE  = "not_applicable"

PDF_ERROR_STATUS_LOOKUP = {
    "ForbiddenError"    : PDFStatus.FORBIDDEN,
    "NotFoundError"     : PDFStatus.NOT_FOUND,
}