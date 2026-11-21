from toolmate.diagnostics.logger import configure_logging


def test_configure_logging_writes_to_file_and_is_idempotent(tmp_path):
    log_path = tmp_path / "toolmate.log"
    logger = configure_logging(tmp_path)
    file_handler = next(
        handler
        for handler in logger.handlers
        if getattr(handler, "baseFilename", None) == str(log_path.resolve())
    )
    handler_count = len(logger.handlers)

    try:
        assert configure_logging(tmp_path) is logger
        assert len(logger.handlers) == handler_count
        logger.info("persistent log test")
        file_handler.flush()

        assert "persistent log test" in log_path.read_text(encoding="utf-8")
    finally:
        logger.removeHandler(file_handler)
        file_handler.close()
