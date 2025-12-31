// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Base Page Object
// All page objects inherit from this class
// ═══════════════════════════════════════════════════════════════════

export class BasePage {
  /**
   * Wait for element to be displayed
   */
  async waitForDisplayed(selector: string, timeout = 10000): Promise<void> {
    const element = await $(selector);
    await element.waitForDisplayed({ timeout });
  }

  /**
   * Wait for element to be clickable
   */
  async waitForClickable(selector: string, timeout = 10000): Promise<void> {
    const element = await $(selector);
    await element.waitForClickable({ timeout });
  }

  /**
   * Click element with wait
   */
  async click(selector: string): Promise<void> {
    await this.waitForClickable(selector);
    const element = await $(selector);
    await element.click();
  }

  /**
   * Set value in input field
   */
  async setValue(selector: string, value: string | number): Promise<void> {
    await this.waitForDisplayed(selector);
    const element = await $(selector);
    await element.setValue(value);
  }

  /**
   * Clear and set value
   */
  async clearAndSetValue(selector: string, value: string | number): Promise<void> {
    await this.waitForDisplayed(selector);
    const element = await $(selector);
    await element.clearValue();
    await element.setValue(value);
  }

  /**
   * Get text from element
   */
  async getText(selector: string): Promise<string> {
    await this.waitForDisplayed(selector);
    const element = await $(selector);
    return await element.getText();
  }

  /**
   * Check if element exists
   */
  async exists(selector: string): Promise<boolean> {
    const element = await $(selector);
    return await element.isExisting();
  }

  /**
   * Check if element is visible
   */
  async isVisible(selector: string): Promise<boolean> {
    const element = await $(selector);
    return await element.isDisplayed();
  }

  /**
   * Wait for text to be present
   */
  async waitForText(selector: string, expectedText: string, timeout = 10000): Promise<void> {
    const element = await $(selector);
    await browser.waitUntil(
      async () => {
        const text = await element.getText();
        return text.includes(expectedText);
      },
      {
        timeout,
        timeoutMsg: `Expected element "${selector}" to contain text "${expectedText}"`,
      }
    );
  }

  /**
   * Wait for condition
   */
  async waitUntil(
    condition: () => Promise<boolean> | boolean,
    options?: { timeout?: number; timeoutMsg?: string }
  ): Promise<void> {
    await browser.waitUntil(condition, {
      timeout: options?.timeout || 10000,
      timeoutMsg: options?.timeoutMsg || 'Condition not met within timeout',
    });
  }

  /**
   * Take screenshot
   */
  async takeScreenshot(filename: string): Promise<void> {
    await browser.saveScreenshot(`./e2e/data/screenshots/${filename}.png`);
  }

  /**
   * Pause execution (for debugging)
   */
  async pause(milliseconds: number): Promise<void> {
    await browser.pause(milliseconds);
  }

  /**
   * Scroll element into view
   */
  async scrollIntoView(selector: string): Promise<void> {
    const element = await $(selector);
    await element.scrollIntoView();
  }

  /**
   * Get attribute value
   */
  async getAttribute(selector: string, attributeName: string): Promise<string | null> {
    const element = await $(selector);
    return await element.getAttribute(attributeName);
  }

  /**
   * Check if element is enabled
   */
  async isEnabled(selector: string): Promise<boolean> {
    const element = await $(selector);
    return await element.isEnabled();
  }

  /**
   * Double click
   */
  async doubleClick(selector: string): Promise<void> {
    await this.waitForClickable(selector);
    const element = await $(selector);
    await element.doubleClick();
  }

  /**
   * Right click (context menu)
   */
  async rightClick(selector: string): Promise<void> {
    await this.waitForClickable(selector);
    const element = await $(selector);
    await element.click({ button: 'right' });
  }

  /**
   * Select dropdown option by value
   */
  async selectByValue(selector: string, value: string): Promise<void> {
    await this.waitForDisplayed(selector);
    const element = await $(selector);
    await element.selectByAttribute('value', value);
  }

  /**
   * Select dropdown option by text
   */
  async selectByText(selector: string, text: string): Promise<void> {
    await this.waitForDisplayed(selector);
    const element = await $(selector);
    await element.selectByVisibleText(text);
  }

  /**
   * Get count of elements matching selector
   */
  async getElementCount(selector: string): Promise<number> {
    const elements = await $$(selector);
    return elements.length;
  }

  /**
   * Check if checkbox/radio is selected
   */
  async isSelected(selector: string): Promise<boolean> {
    const element = await $(selector);
    return await element.isSelected();
  }
}
