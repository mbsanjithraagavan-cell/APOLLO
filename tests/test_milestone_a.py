from app.graph import build_graph
from app.safety import sanitize_pii


def test_sanitizer_redacts_contact_data():
    result = sanitize_pii("Book cardiology; email alice@example.com, phone +91 98765 43210")
    assert "alice@example.com" not in result.text
    assert result.redaction_count >= 2


def test_graph_booking_routes_without_side_effects():
    result = build_graph().invoke({"sanitized_input": "I want to book a cardiologist tomorrow afternoon."})
    assert result["intent"] == "booking"
    assert result["status"] == "needs_integration"
    assert "booking_intent" in result


def test_emergency_halts_before_routing():
    result = build_graph().invoke({"sanitized_input": "I have chest pain and need an appointment."})
    assert result["status"] == "emergency"
    assert "booking_intent" not in result


def test_clinical_request_is_out_of_scope():
    result = build_graph().invoke({"sanitized_input": "Should I change my medication dose?"})
    assert result["status"] == "escalated"
