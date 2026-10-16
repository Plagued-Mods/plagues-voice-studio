"""Sequential background rendering and cooperative chunk-level cancellation."""
from __future__ import annotations
from threading import Event
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from .engine import Engine, GenerationCancelled
from .jobs import NarrationJob
from .error_messages import friendly_generation_error


class RenderWorker(QObject):
    message = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    job_started = pyqtSignal(str)
    job_finished = pyqtSignal(str, str, str)  # id, output, error
    done = pyqtSignal()

    def __init__(self, jobs: list[NarrationJob]):
        super().__init__()
        self.jobs = jobs[:]
        self.cancel_event = Event()

    def cancel(self):
        self.cancel_event.set()

    @pyqtSlot()
    def run(self):
        engine = Engine()
        try:
            for job in self.jobs:
                if self.cancel_event.is_set():
                    break
                self.job_started.emit(job.job_id)
                try:
                    path = engine.render(
                        job, self.message.emit,
                        lambda count, total: self.progress.emit(count, total),
                        self.cancel_event.is_set,
                    )
                except GenerationCancelled:
                    self.job_finished.emit(job.job_id, "", "Cancelled")
                    break
                except Exception as exc:
                    message = friendly_generation_error(exc)
                    self.job_finished.emit(job.job_id, "", message)
                    self.message.emit(f"ERROR: {message}")
                else:
                    self.job_finished.emit(job.job_id, str(path), "")
        finally:
            self.done.emit()
