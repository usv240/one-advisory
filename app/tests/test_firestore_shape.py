from one_advisory.workflow import create_incident


def _has_nested_array(value):
    if isinstance(value, list):
        return any(isinstance(item, list) or _has_nested_array(item) for item in value)
    if isinstance(value, dict):
        return any(_has_nested_array(item) for item in value.values())
    return False


def test_incident_avoids_firestore_nested_arrays():
    incident = create_incident()
    assert not _has_nested_array(incident)
    assert all(set(point) == {"x", "y"} for point in incident["advisory"]["zone"]["polygon"])
