import logging


class EndpointFilter(logging.Filter):
    _allowed_methods = {
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "HEAD",
        "OPTIONS",
        "TRACE",
    }

    def __init__(
        self, exclude_path: str, exclude_method: str, exclude_status: int = None
    ):
        if not exclude_path.startswith("/"):
            raise ValueError("exclude_path must start with '/'")
        if exclude_method not in self._allowed_methods:
            raise ValueError(f"Invalid method: {exclude_method}")

        self.exclude_path = exclude_path
        self.exclude_method = exclude_method
        self.exclude_status = exclude_status

    def filter(self, record: logging.LogRecord) -> bool:
        if record.args and len(record.args) >= 4:
            method = record.args[1]
            path = record.args[2]
            status = record.args[4]

            if (
                path == self.exclude_path
                and method == self.exclude_method
                and (not self.exclude_status or self.exclude_status == status)
            ):
                return False
        return True
