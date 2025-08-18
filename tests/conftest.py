import logging
import pytest
from loguru import logger

from _pytest.logging import LogCaptureFixture

@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,  # Set to 'True' if your test is spawning child processes.
    )
    yield caplog
    logger.remove(handler_id)

@pytest.fixture
def reportlog(pytestconfig):
    logging_plugin = pytestconfig.pluginmanager.getplugin("logging-plugin")
    handler_id = logger.add(logging_plugin.report_handler, format="{message}")
    yield
    logger.remove(handler_id)


@pytest.fixture(autouse=True)
def propagate_logs():
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            if logging.getLogger(record.name).isEnabledFor(record.levelno):
                logging.getLogger(record.name).handle(record)

    logger.remove()
    logger.add(PropagateHandler(), format="{message}")
    yield


def pytest_collection_modifyitems(config, items):
    """ Adds pytest.mark.explicit for test that only should run when called explicitly

    Code mainly from https://stackoverflow.com/a/56379871
    """
    if config.option.keyword or config.option.markexpr:
        return

    skip_explicit = pytest.mark.skip(reason='Test explicitly not selected')
    for item in items:
        if 'explicit' in item.keywords and not any([str(a).endswith(f'::{item.name}') for a in config.args]):
            item.add_marker(skip_explicit)
