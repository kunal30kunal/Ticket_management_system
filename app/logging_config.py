import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    filename="app.log",
    filemode="a"
)

logger = logging.getLogger("ticket_app")