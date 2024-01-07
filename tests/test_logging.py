import logging


from inspira.logging import log, handler


def test_logging():
    assert log.name == "Inspira"
    assert log.level == logging.INFO
    assert log.handlers == [handler]


def test_logger_error():
    log.level = logging.ERROR
    assert log.level == logging.ERROR
    assert log.handlers == [handler]
