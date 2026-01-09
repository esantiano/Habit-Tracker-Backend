from datetime import date

def test_dashboard_today_returns_habits_and_completion(client, auth_headers):
    initial = client.get("/dashboard/today", headers=auth_headers)
    assert initial.status_code == 200, initial.text
    today_str = initial.json()["date"]

    habit_payload_1 = {
        "name":"Workout",
        "description:":"",
        "goal_type":"DAILY",
        "target_per_period":1,
        "start_date":today_str,
    }

    habit_payload_2 = {
        "name":"Mediate",
        "description":"",
        "goal_type":"DAILY",
        "target_per_period":1,
        "start_date":today_str,
    }

    h1_res = client.post("/habits/", json=habit_payload_1, headers=auth_headers)
    assert h1_res .status_code == 201, h1_res.text
    h1 = h1_res.json()
    
    h2_res = client.post("/habits/", json=habit_payload_2, headers=auth_headers)
    assert h2_res.status_code == 201, h2_res.text
    h2 = h2_res.json()

    log_res = client.post(
        f"/habits/{h1['id']}/logs",
        json={"date": today_str, "value":1},
        headers=auth_headers,
    )
    assert log_res.status_code == 201, log_res.text

    res = client.get("/dashboard/today", headers=auth_headers)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["date"] == today_str
    assert isinstance(data["habits"], list)
    assert len(data["habits"]) >= 2

    by_id = {item["habit"]["id"]: item for item in data["habits"]}
    assert by_id[h1["id"]]["is_completed"] is True
    assert by_id[h2["id"]]["is_completed"] is False