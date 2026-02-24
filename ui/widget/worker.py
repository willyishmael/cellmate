from PySide6.QtCore import QThread, Signal


class Worker(QThread):
    """A reusable worker thread for running long-running operations without blocking the UI."""
    
    finished = Signal(object)  # Emits the result
    error = Signal(str)         # Emits error message

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            result = self.func(*self.args)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
