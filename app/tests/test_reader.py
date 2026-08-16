from one_advisory.reader import AdvisoryReader, ReplayAdvisoryClient


def test_advisory_reader_retains_only_quoted_fields():
    reader = AdvisoryReader(ReplayAdvisoryClient({"transcription":"ACTIVE East zone","fields":[{"key":"status","value":"active","quote":"ACTIVE","confidence":.9},{"key":"zone","value":"invented","quote":"West zone","confidence":.9}]}))
    result = reader.read(b"fixture")
    assert len(result.fields) == 1
    assert len(result.dropped) == 1


def test_advisory_reader_requires_document_and_transcript():
    reader = AdvisoryReader(ReplayAdvisoryClient({"transcription":"","fields":[]}))
    for document, message in [(b"","document"),(b"x","transcription")]:
        try: reader.read(document)
        except ValueError as exc: assert message in str(exc)
        else: raise AssertionError("invalid advisory should fail")

