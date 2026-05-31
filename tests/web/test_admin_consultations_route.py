def test_admin_consultations_page_opens(client):
    """
    Test case: open consultation entitlements admin page.

    What we verify:
    - Admin consultations route is reachable.
    - Template renders empty state.
    """

    response = client.get("/admin/consultations")

    assert response.status_code == 200
    assert "Consultation entitlements" in response.text
    assert "No consultation entitlements found." in response.text