from datetime import date

def test_create_habit_authenticated(client, auth_headers):
    payload = {
        "name":"Workout",
        "description":"Calisthenics",
        "goal_type":"DAILY",
        "target_per_period":1,
        "start_date":str(date.today()),
    }
    res = client.post("/habits/", json=payload, headers=auth_headers)
    assert res.status_code == 201, res.text
    habit = res.json()

    assert habit["name"] == "Workout"
    assert habit["is_archived"] is False
    assert "id" in habit

def test_create_habit_log_for_today(client, auth_headers):
    habit_payload = {
        "name":"Read",
        "description":"10 pages",
        "goal_type":"DAILY",
        "target_per_period":1,
        "start_date": str(date.today()),
    }

    hres = client.post("/habits/", json=habit_payload, headers=auth_headers)
    assert hres.status_code == 201, hres.text
    habit_id = hres.json()["id"]

    log_payload = {"date":str(date.today()), "value":1}
    lres = client.post(f"/habits/{habit_id}/logs", json=log_payload, headers=auth_headers)
    assert lres.status_code == 201, lres.text
    log = lres.json()

    assert log["habit_id"] == habit_id
    assert log["date"] == str(date.today())