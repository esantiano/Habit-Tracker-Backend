from datetime import date, timedelta

def test_stats_overview_returns_shape(client, auth_headers):
    today = date.today()
    hres = client.post(
        "/habits/",
        json={
            "name": "Workout",
            "description" : "",
            "goal_type" : "DAILY",
            "target_per_period" : 1,
            "start_date" : str(today)
        },
        headers=auth_headers,
    )
    assert hres.status_code == 201, hres.text
    habit_id = hres.json()["id"]

    lres = client.post(
        f"/habits/{habit_id}/logs",
        json={"date": str(today), "value":1},
        headers=auth_headers,
    )
    assert lres.status_code == 201, lres.text
    res = client.get("stats/overview?range=7d", headers=auth_headers)
    assert res.status_code == 200, res.text

    data = res.json()
    assert "overall_completion_rate" in data
    assert "habits" in data
    assert len(data["habits"]) >= 1