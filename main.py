"""Main entry point for The AGI Assistant."""

import sys
import traceback
from src.ui.main_window import MainWindow
from src.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main application entry point."""
    try:
        logger.info("Starting The AGI Assistant")
        
        # Create and run main window
        app = MainWindow()
        
        # Handle window closing
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start main loop
        app.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("Application closed")


if __name__ == "__main__":
    main()

