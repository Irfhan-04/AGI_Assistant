"""Browser automation actions using Playwright."""

import time
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from src.logger import get_logger

logger = get_logger(__name__)


class BrowserActions:
    """Browser automation actions wrapper."""
    
    def __init__(self):
        """Initialize browser actions."""
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        logger.info("Browser actions initialized")
    
    def _ensure_browser(self):
        """Ensure browser is launched."""
        if self.playwright is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            logger.info("Browser launched")
    
    def navigate(self, url: str) -> bool:
        """Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful
        """
        try:
            self._ensure_browser()
            self.page.goto(url)
            logger.info(f"Navigated to: {url}")
            time.sleep(1)  # Wait for page to load
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    def click_element(self, selector: str) -> bool:
        """Click an element by CSS selector.
        
        Args:
            selector: CSS selector
            
        Returns:
            True if successful
        """
        try:
            self._ensure_browser()
            self.page.click(selector)
            logger.debug(f"Clicked element: {selector}")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Error clicking element {selector}: {e}")
            return False
    
    def fill_input(self, selector: str, text: str) -> bool:
        """Fill an input field.
        
        Args:
            selector: CSS selector for input
            text: Text to fill
            
        Returns:
            True if successful
        """
        try:
            self._ensure_browser()
            self.page.fill(selector, text)
            logger.debug(f"Filled input {selector} with: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error filling input {selector}: {e}")
            return False
    
    def select_option(self, selector: str, value: str) -> bool:
        """Select an option in a dropdown.
        
        Args:
            selector: CSS selector for dropdown
            value: Option value to select
            
        Returns:
            True if successful
        """
        try:
            self._ensure_browser()
            self.page.select_option(selector, value)
            logger.debug(f"Selected option {value} in {selector}")
            return True
        except Exception as e:
            logger.error(f"Error selecting option in {selector}: {e}")
            return False
    
    def get_text(self, selector: str) -> Optional[str]:
        """Get text content of an element.
        
        Args:
            selector: CSS selector
            
        Returns:
            Text content or None
        """
        try:
            self._ensure_browser()
            text = self.page.text_content(selector)
            return text
        except Exception as e:
            logger.error(f"Error getting text from {selector}: {e}")
            return None
    
    def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for an element to appear.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
            
        Returns:
            True if element found
        """
        try:
            self._ensure_browser()
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Error waiting for element {selector}: {e}")
            return False
    
    def close(self):
        """Close browser."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

