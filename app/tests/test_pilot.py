from one_advisory.pilot import create_pilot_incident


def payload():
    return {
        "synthetic_acknowledgement": True,
        "data_class": "synthetic",
        "advisory": {
            "title": "North zone boil-water exercise",
            "authority": "Taylor Morgan, exercise commander - fictional",
            "issued_at": "2026-08-17T10:00:00Z",
            "zone_name": "North service zone - fictional",
            "source_title": "Exercise advisory bulletin",
            "source_url": "https://example.test/advisory",
        },
        "facilities": [
            {"type": "dialysis", "name": "North Dialysis - fictional", "contact": "Charge lead - fictional", "capacity_note": "12 stations"},
            {"type": "school_childcare", "name": "North Learning Center - fictional", "contact": "Site lead - fictional", "capacity_note": "180 learners"},
            {"type": "long_term_care", "name": "North Care Home - fictional", "contact": "Administrator - fictional", "capacity_note": "64 residents"},
        ],
    }


def test_custom_incident_preserves_supplied_synthetic_facts():
    incident = create_pilot_incident(payload())
    assert incident["origin"] == "pilot_input"
    assert incident["data_class"] == "synthetic"
    assert incident["advisory"]["title"] == "North zone boil-water exercise"
    assert [row["name"] for row in incident["facilities"]] == [
        "North Dialysis - fictional",
        "North Learning Center - fictional",
        "North Care Home - fictional",
    ]
    assert incident["safety"]["system_issued_advisory"] is False
    assert len(incident["incident_id"]) > 30


def test_custom_incident_rejects_non_synthetic_or_wrong_roster():
    bad = payload()
    bad["data_class"] = "real"
    try:
        create_pilot_incident(bad)
        assert False
    except ValueError as exc:
        assert "synthetic" in str(exc)
    bad = payload()
    bad["facilities"] = bad["facilities"][:2]
    try:
        create_pilot_incident(bad)
        assert False
    except ValueError as exc:
        assert "dialysis" in str(exc)
