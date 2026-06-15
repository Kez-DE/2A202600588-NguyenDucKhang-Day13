from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_pii() -> None:
    out = scrub_text("Phone 0987654321 CCCD 012345678901 card 4111 1111 1111 1111 passport B12345678")
    assert "0987654321" not in out
    assert "012345678901" not in out
    assert "4111" not in out
    assert "B12345678" not in out
    assert "REDACTED_PHONE_VN" in out
    assert "REDACTED_CCCD" in out
    assert "REDACTED_CREDIT_CARD" in out
    assert "REDACTED_PASSPORT" in out
