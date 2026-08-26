import json

import volsegtools as vst


def test_standard_reporter(capsys):
    timer = vst.Timer()
    timer.push_stage("test_stage")
    timer.push_event("test_event")
    timer.pop_event()
    timer.pop_stage()
    timer.print_report(vst.StandardReporter())
    out, _ = capsys.readouterr()

    expected = (
        "--------------------------------------------------------------\n"
        "Time Report, total time = 0.0s\n"
        "--------------------------------------------------------------\n"
        "( 0.000%) Stage: 'test_stage' (0.000s / 0.000s / 0.000s)\n"
        "( 0.000% /  0.000%) Event: 'test_event' (0.000s / 0.000s / 0.000s)\n"
    )

    assert out == expected


def test_json_reporter(tmp_path):
    timer = vst.Timer()
    timer.push_stage("test_stage")
    timer.push_event("test_event")
    timer.pop_event()
    timer.pop_stage()

    output_file = tmp_path / "json_report.json"

    timer.print_report(
        vst.JSONTimerReporter(
            output_path=output_file,
            label="input_file_name",
            method="some_method",
        )
    )

    with open(output_file) as file:
        data = json.load(file)

    assert data[0]["kind"] == "stage"
    assert data[0]["label"] == "input_file_name"
    assert data[0]["method"] == "some_method"
    assert data[0]["text"] == "test_stage"
    assert data[0]["total_time"] == 0.0

    assert data[0].get("stage_id", None) != None
    assert data[0].get("timer_id", None) != None
    assert data[0].get("timestamp", None) != None

    assert data[1]["kind"] == "event"
    assert data[1]["label"] == "input_file_name"
    assert data[1]["method"] == "some_method"
    assert data[1]["text"] == "test_event"
    assert data[1]["total_time"] == 0.0

    assert data[1].get("stage_id", None) != None
    assert data[1].get("timer_id", None) != None
    assert data[1].get("timestamp", None) != None
