import logging
import json
import os
from logging import LogRecord
from collections import defaultdict
from teams_logger import TeamsHandler, TeamsCardsFormatter #pip install teams-logger
import datetime
from traceback import format_exception

WEBHOOK_URL = "Your webhook url goes here"

def _addLoggingLevel(levelName, levelNum):
    # https://stackoverflow.com/a/35804945
    methodName = levelName.lower()

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

class CardFormatter(TeamsCardsFormatter):
    """
    This formatter formats logs records as a simple office 365 connector card.
    The connector card documentation is displayed in the link below:
    https://docs.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-reference#office-365-connector-card
    """
    # Copy/paste from Office365CardFormatter of teams_logger
    # Facts removed, filelist to be passed into facts section.
    _color_map = defaultdict(lambda: "#008000", {
        "DEBUG": "#0000FF",  # blue
        "INFO": "#008000",  # green
        "WARNING": "#FFA500",  # orange
        "ERROR": "#FF0000",  # red
        "CRITICAL": "#8B0000",  # darkred
    })

    def __init__(self):
        super().__init__()

    def format(self, record: LogRecord) -> str:
        message = record.getMessage()
        if record.exc_info:
            etype, value, tb = record.exc_info
            message += '\n' * 2
            message += '<code>'
            message += ''.join(format_exception(etype, value, tb))
            message += '</code>'
        output= json.dumps({
            "@context": "https://schema.org/extensions",
            "@type": "MessageCard",
            "title": record.name,
            "summary": message,
            "sections": [
                {"facts": self._build_file_list(record)}
            ] if hasattr(record, 'outputList') else "",
            # Fallback to INFO color if needed
            "themeColor": self._color_map[record.levelname],
            "text": message,
        })
        return output

    def _build_file_list(self, record: LogRecord):
        return [{
            "name": os.path.split(f)[1],
            "value": "<a href='" + f + "'>" + f + "</a>"
        } for f in record.outputList]


def start(loggerName, level=logging.INFO):
    # TEAMS logging level added above INFO, so that TEAMS logger will not receive all INFOs that go in the file log,
    # only a single post at the end of the run plus warnings and critical messages
    _addLoggingLevel("TEAMS", logging.INFO + 5)
    logging.basicConfig(filename='logs\\' + loggerName + "_" + datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S") + '.log', 
                        encoding='utf-8',  level=level, format='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    log = logging.getLogger(loggerName)

    #Url pointing to Incomming Webhook from Teams connector
    th = TeamsHandler(url=WEBHOOK_URL,level=logging.TEAMS)
    cf = CardFormatter()
    th.setFormatter(cf)
    log.addHandler(th)
    return log

if __name__ == "__main__":
    pass