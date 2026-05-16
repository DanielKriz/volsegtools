from typing import List, Optional, Any
from pathlib import Path
import datetime
import logging
import json
import time
import uuid


vst_logger = logging.getLogger("volsegtools")


class Timer:
    class Stage:
        def __init__(self, name):
            self.events: List[Timer.Event] = []
            self.start = time.time()
            self.end: Optional[float] = None
            self.name = name

        def push_event(self, name):
            if len(self.events) != 0:
                self.events.append(Timer.Event(self.events[-1].end, name, self))
            else:
                self.events.append(Timer.Event(self.start, name, self))

        def pop_event(self):
            if len(self.events) == 0:
                return
            if self.events[-1].end is None:
                self.events[-1].end = time.time()

        @property
        def total_time(self) -> float:
            return self.end - self.start

        def serialize(self, use_ms=False):
            self.pop_event()
            return {
                "type": "stage",
                "time": self.end
                if not use_ms
                else round(
                    self.total_time,
                    Timer.RESOLUTION,
                ),
                "name": self.name,
                "events": [e.serialize(use_ms) for e in self.events],
            }

    class Event:
        def __init__(self, start, name: str, parent: Optional[Any] = None):
            self.parent: Optional[Timer.Stage] = parent
            self.name: str = name
            self.start = start
            self.end = time.time()

        def serialize(self, use_ms=False):
            return {
                "type": "event",
                "name": self.name,
                "time": self.end
                if not use_ms
                else round(
                    self.total_time,
                    Timer.RESOLUTION,
                ),
            }

        @property
        def total_time(self) -> float:
            return self.end - self.start

    RESOLUTION = 3

    start = time.time()
    points: List[Stage | Event] = []
    current_stage: Optional[Stage] = None
    current_event: Optional[Event] = None

    @staticmethod
    def restart():
        Timer.start = time.time()
        Timer.points = []

    @staticmethod
    def push_stage(name: str):
        if Timer.current_stage is not None:
            Timer.pop_stage()
        Timer.current_stage = Timer.Stage(name)
        Timer.points.append(Timer.current_stage)

    @staticmethod
    def pop_stage():
        if Timer.current_stage is not None:
            Timer.current_stage.end = time.time()
            Timer.current_stage = None

    @staticmethod
    def pop_event():
        if Timer.current_stage is not None:
            Timer.current_stage.pop_event()
        elif len(Timer.points) != 0:
            Timer.points[-1].end = time.time()

    @staticmethod
    def push_event(name: str):
        if Timer.current_stage is not None:
            Timer.current_stage.push_event(name)
            Timer.current_event = Timer.current_stage.events[-1]
        else:
            Timer.current_event = Timer.Event(name)
            Timer.points.append(Timer.current_event)

    @staticmethod
    def total_time():
        return Timer.start + sum([p.end - p.start for p in Timer.points])

    @staticmethod
    def serialize(use_ms=False):
        Timer.pop_stage()
        return {
            "total_time": round(Timer.total_time() - Timer.start, Timer.RESOLUTION)
            if use_ms
            else Timer.total_time(),
            "stamps": [p.serialize(use_ms) for p in Timer.points],
        }

    @staticmethod
    def print_report(reporter):
        reporter.report(Timer.serialize(True))


class TimerReporter:
    STAGE_FMT = "({:6.3f}%) Stage: '{}' ({:0.3f}s / {:0.3f}s / {:0.3f}s)"
    EVENT_FMT = "({:6.3f}% / {:6.3f}%) Event: '{}' ({:0.3f}s / {:0.3f}s / {:0.3f}s)"

    def to_percent(self, part, total):
        step = total / 100.0
        return part / step

    def report(self, timer_data):
        total_time = timer_data["total_time"]

        print("--------------------------------------------------------------")
        print(f"Time Report, total time = {total_time}s")
        print("--------------------------------------------------------------")

        cummulative_total = 0.0

        for stamp in timer_data["stamps"]:
            cummulative_total += stamp["time"]
            if stamp["type"] == "stage":
                self.report_stage(stamp, timer_data["total_time"], cummulative_total)
            else:
                self.report_event(stamp, total_time, 100, cummulative_total, orhan=True)

    def report_stage(self, stage, total, cummulative_total):
        print(
            self.STAGE_FMT.format(
                self.to_percent(stage["time"], total),
                stage["name"],
                stage["time"],
                cummulative_total,
                total,
            )
        )
        cummulative_time = 0.0
        for event in stage["events"]:
            cummulative_time += event["time"]
            self.report_event(event, total, stage["time"], cummulative_time)

    def report_event(self, event, total, total_stage, cummulative, orhan=False):
        fmt_str = self.EVENT_FMT if not orhan else "- " + self.EVENT_FMT
        print(
            fmt_str.format(
                self.to_percent(event["time"], total),
                self.to_percent(event["time"], total_stage),
                event["name"],
                event["time"],
                cummulative,
                total_stage,
            )
        )


class JSONTimerReporter:
    def __init__(self, output_path: Path, label: str, **kwargs):
        self.label = label
        self.output_path = output_path
        self.uuid = uuid.uuid1()
        self.time = datetime.datetime.now()
        self.additional_columns = kwargs

    def create_record(self, kind, text, total_time, stage=-1):
        record = {
            "label": self.label,
            "timestamp": f"{self.time}",
            "timer_id": str(self.uuid),
            "stage_id": stage,
            "kind": kind,
            "text": text,
            "total_time": total_time,
        }

        if self.additional_columns != {}:
            record.update(self.additional_columns)

        return record

    def report(self, timer_data):
        records = []
        stage_idx = 1
        for stamp in timer_data["stamps"]:
            if stamp["type"] == "stage":
                records.append(
                    self.create_record(
                        kind="stage",
                        text=stamp["name"],
                        total_time=stamp["time"],
                    )
                )
                for event in stamp["events"]:
                    records.append(
                        self.create_record(
                            kind="event",
                            text=event["name"],
                            total_time=event["time"],
                            stage=stage_idx,
                        )
                    )
                stage_idx += 1
            else:
                records.append(
                    self.create_record(
                        kind="event",
                        text=stamp["name"],
                        total_time=stamp["time"],
                        stage=0,
                    )
                )

        # TODO: if json parsing fails, we need some behavior (forceful overwrite?)
        if self.output_path.exists():
            with open(self.output_path, "r") as file:
                old_records = json.load(file)
                records += old_records

        with open(self.output_path, "w") as file:
            file.write(json.dumps(records, indent=2))

        vst_logger.info(
            "Finished writing timer report into {}".format(self.output_path)
        )
