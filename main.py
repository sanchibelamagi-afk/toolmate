import sys

from src.toolmate.diagnostics.logger import configure_logging
from src.toolmate.tui.app import main


if __name__ == "__main__":
    configure_logging()
    sys.exit(main())
