from pathlib import Path
from typing import Any, Protocol

import datetime
import json
import logging
import math
import time
import uuid

vst_logger = logging.getLogger("volsegtools")


class TimerReporter(Protocol):
    """Used for reporting of the timer data."""

    def report(self, timer_data: dict) -> None:
        """Reports the timer data in some fashion.

        Parameters
        ----------
        timer_data: dict
            The measurement data from the timer that should be reported.
        """
        ...


class Timer:
    """Timer for measuring processing time of stages and events.

    Attributes
    ----------
    RESOLUTION: int
        How many decimal numbers are considered.
    start: float
        Unix time denoting the start of measurement collection.
    points: list[Timer.Stage | Timer.Event]
        List of all measurements.
    current_event: Timer.Event | None
        Current event measurement, if there is any.
    current_stage: Timer.Stage | None
        Current stage measurement, if there is any.
    """

    RESOLUTION = 3

    class Stage:
        """Represents a single stage measurement in a pipeline.

        Attributes
        ----------
        events: list[Timer.Event]
            List of events that have happened during this stage.
        start: float
            Unix time denoting the start of this stage.
        end: float
            Unix time denoting the end of this stage.
        name: str
            Name of this stage.
        """

        def __init__(self, name: str):
            self.events: list[Timer.Event] = []
            self.start: float = time.time()
            self.end: float | None = None
            self.name: str = name

        def push_event(self, name: str) -> None:
            """Adds named event to this stage.

            Parameters
            ----------
            name: str
                Name of the event.
            """
            if len(self.events) != 0:
                self.events.append(Timer.Event(self.events[-1].end, name, self))
            else:
                self.events.append(Timer.Event(self.start, name, self))

        def pop_event(self) -> None:
            """Pops the current active event.

            Basically marks the event a finished, if there is any.

            If there is no current event, then it simply does nothing.
            """
            if len(self.events) == 0:
                return
            if self.events[-1].end is None:
                self.events[-1].end = time.time()

        @property
        def total_time(self) -> float:
            """Calculates the total time of the stage.

            The stage has to be finished to calculate the total time.

            Raises
            ------
            RuntimeError:
                if the stage is not finished.

            Returns
            -------
            float
                The total time spent in the stage.
            """
            if self.end is None:
                raise RuntimeError("There was not measurement")
            return self.end - self.start

        def serialize(self, use_ms: bool = False) -> dict:
            """Serializes the current stage into a dictionary.

            Parameters
            ----------
            use_ms: bool
                Flag that denotes whether the result should be saved in Unix
                time or in miliseconds.

            Returns
            -------
            dict:
                Serialized stage.
            """
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
        """Represents an single event measurement of a stage or pipeline.

        Key difference from the stage is that the event happens once, it is not
        a continuous part of the timeline.

        Therefore, it is immediatelly ended and for the calculation of total
        time we need the start time of the parent stage/start of the timer
        measurement.

        Attributes
        ----------
        parent: Timer.Stage | None
            Reference to the parent stage of this event. If there is none,
            then the event has happened outside of any stage.
        name: str
            Name of the event.
        start: float
            Unix time denoting the start of the stage.
        end: float
            Unix time denoting the end of this event.
        """

        def __init__(self, start: float, name: str, parent: Any | None = None):
            self.parent: Timer.Stage | None = parent
            self.name: str = name
            self.start: float = start
            self.end: float = time.time()

        def serialize(self, use_ms=False) -> dict:
            """Serializes the current event into a dictionary.

            Parameters
            ----------
            use_ms: bool
                Flag that denotes whether the result should be saved in Unix
                time or in miliseconds.

            Returns
            -------
            dict:
                Serialized event.
            """
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
            """Calculates the total time of the event.

            In comparison of a stage, event is not continuous and is always
            ended.

            Returns
            -------
            float
                The total time spent in the event.
            """
            return self.end - self.start

    def __init__(self):
        self.start = time.time()
        self.points: list[Timer.Stage | Timer.Event] = []
        self.current_event: Timer.Event | None = None
        self.current_stage: Timer.Stage | None = None

    def restart(self) -> None:
        """Clears taken measurements and resets the start time point."""
        self.start = time.time()
        self.points = []

    def push_stage(self, name: str) -> None:
        """Adds named stage measurement.

        Parameters
        ----------
        name: str
            Name of the stage.
        """
        if self.current_stage is not None:
            self.pop_stage()
        self.current_stage = Timer.Stage(name)
        self.points.append(self.current_stage)

    def pop_stage(self):
        """Pops the current active stage.

        Marks the stage as finished. If there is none, then it does nothing.
        """
        if self.current_stage is not None:
            self.current_stage.end = time.time()
            self.current_stage = None

    def pop_event(self):
        """Pops the current active event.

        Marks the event as finished. If there is none, then it does nothing.
        """
        if self.current_stage is not None:
            self.current_stage.pop_event()
        elif len(self.points) != 0:
            self.points[-1].end = time.time()

    def push_event(self, name: str):
        """Adds named event measurement.

        If there is current stage present, then this operation is delegated.
        Otherwise the timer is the owner of this measurement.

        Parameters
        ----------
        name: str
            Name of the event.
        """
        if self.current_stage is not None:
            self.current_stage.push_event(name)
            self.current_event = self.current_stage.events[-1]
        else:
            self.current_event = Timer.Event(name)
            self.points.append(self.current_event)

    def total_time(self) -> float:
        """Calculated the total time of the whole measurement.

        Raises
        ------
        RuntimeError:
            if any of the measurement points is not ended.

        Returns
        -------
        float:
            The total time of the whole measurement.
        """

        def calculate_partial_time(start: float, end: float | None) -> float:
            if end is None:
                raise RuntimeError("There was not measurement")
            return end - start

        return self.start + sum(
            [calculate_partial_time(p.start, p.end) for p in self.points]
        )

    def serialize(self, use_ms: bool = False) -> dict:
        """Serializes the whole timer's measurement into a directory"""
        self.pop_stage()
        return {
            "total_time": round(self.total_time() - self.start, Timer.RESOLUTION)
            if use_ms
            else self.total_time(),
            "stamps": [p.serialize(use_ms) for p in self.points],
        }

    def print_report(self, reporter: TimerReporter) -> None:
        """Prints the measurements using some reporter.

        Parameters
        ----------
        reporter: TimerReporter
            Instance of timer reporter to which is delegated the reporting.
        """
        reporter.report(self.serialize(True))


class StandardReporter(TimerReporter):
    """Reporter to the stdout."""

    STAGE_FMT = "({:6.3f}%) Stage: '{}' ({:0.3f}s / {:0.3f}s / {:0.3f}s)"
    EVENT_FMT = "({:6.3f}% / {:6.3f}%) Event: '{}' ({:0.3f}s / {:0.3f}s / {:0.3f}s)"

    def _to_percent(self, part: float, total: float) -> float:
        """Calculates the percentage.

        Parameters
        ----------
        part: float
            ...
        total: float
            ...

        Returns
        -------
        float:
            The percentage in the interval <0, 1.0>.
        """
        step = total / 100.0
        if math.isclose(step, 0):
            return 0.0
        return part / step

    def report(self, timer_data) -> None:
        total_time = timer_data["total_time"]

        print("--------------------------------------------------------------")
        print(f"Time Report, total time = {total_time}s")
        print("--------------------------------------------------------------")

        cummulative_total = 0.0

        for stamp in timer_data["stamps"]:
            cummulative_total += stamp["time"]
            if stamp["type"] == "stage":
                self._report_stage(stamp, timer_data["total_time"], cummulative_total)
            else:
                self._report_event(stamp, total_time, 100, cummulative_total, orhan=True)

    def _report_stage(self, stage, total, cummulative_total):
        print(
            self.STAGE_FMT.format(
                self._to_percent(stage["time"], total),
                stage["name"],
                stage["time"],
                cummulative_total,
                total,
            )
        )
        cummulative_time = 0.0
        for event in stage["events"]:
            cummulative_time += event["time"]
            self._report_event(event, total, stage["time"], cummulative_time)

    def _report_event(self, event, total, total_stage, cummulative, orhan=False):
        fmt_str = self.EVENT_FMT if not orhan else "- " + self.EVENT_FMT
        print(
            fmt_str.format(
                self._to_percent(event["time"], total),
                self._to_percent(event["time"], total_stage),
                event["name"],
                event["time"],
                cummulative,
                total_stage,
            )
        )


class JSONTimerReporter(TimerReporter):
    def __init__(self, output_path: Path, label: str, **kwargs):
        self.label = label
        self.output_path = output_path
        self.uuid = uuid.uuid1()
        self.time = datetime.datetime.now()
        self.additional_columns = kwargs

    def _create_record(self, kind, text, total_time, stage=-1):
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
                    self._create_record(
                        kind="stage",
                        text=stamp["name"],
                        total_time=stamp["time"],
                    )
                )
                for event in stamp["events"]:
                    records.append(
                        self._create_record(
                            kind="event",
                            text=event["name"],
                            total_time=event["time"],
                            stage=stage_idx,
                        )
                    )
                stage_idx += 1
            else:
                records.append(
                    self._create_record(
                        kind="event",
                        text=stamp["name"],
                        total_time=stamp["time"],
                        stage=0,
                    )
                )

        # TODO: if json parsing fails, we need some behavior (forceful overwrite?)
        if self.output_path.exists():
            with Path.open(self.output_path) as file:
                old_records = json.load(file)
                records += old_records

        with Path.open(self.output_path, "w") as file:
            file.write(json.dumps(records, indent=2))

        vst_logger.info(f"Finished writing timer report into {self.output_path}")
