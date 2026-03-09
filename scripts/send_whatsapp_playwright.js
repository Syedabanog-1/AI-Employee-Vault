/**
 * Send a WhatsApp message using Playwright via WhatsApp Web.
 * Uses a persistent Chrome profile so QR scan is only needed once.
 */

const { chromium } = require('playwright');
const path = require('path');
const fs   = require('fs');

const TO_NUMBER = '923322236597';   // no + sign
const MESSAGE   = 'Hi there!';

const CHROME_EXE  = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PROFILE_DIR = path.join(__dirname, 'chrome-whatsapp-profile');

async function snap(page, name) {
  try {
    const p = path.join(__dirname, `${name}.png`);
    await page.screenshot({ path: p });
    console.log('  Screenshot:', p);
  } catch (_) {}
}

(async () => {
  fs.mkdirSync(PROFILE_DIR, { recursive: true });
  console.log('[0] Launching Chrome with persistent WhatsApp profile...');

  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    executablePath: CHROME_EXE,
    headless: false,
    slowMo: 60,
    args: [
      '--start-maximized',
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-infobars',
    ],
    ignoreDefaultArgs: ['--enable-automation'],
  });

  context.on('page', async (p) => {
    await p.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    });
  });

  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });

  try {
    // ── Step 1: Navigate to WhatsApp Web home ─────────────────────────────
    console.log('[1] Navigating to WhatsApp Web...');
    await page.goto('https://web.whatsapp.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    await snap(page, 'wa_s0_initial');
    console.log('    URL:', page.url());

    // ── Step 2: Check if QR code visible (not logged in) ──────────────────
    const chatListSelector = '#side, [data-testid="chat-list"], [data-testid="default-user"], [aria-label="Chat list"], [data-testid="search-input"]';
    const qrCanvasSelector = 'canvas';

    const isLoggedIn = await page.$(chatListSelector);
    if (!isLoggedIn) {
      console.log('\n>>> NOT LOGGED IN — A Chrome window has opened on your screen.');
      console.log('>>> 1. Click on the Chrome window in your taskbar');
      console.log('>>> 2. On your phone: WhatsApp → three dots menu → Linked Devices → Link a Device');
      console.log('>>> 3. Scan the QR code shown in Chrome');
      console.log('>>> Waiting up to 5 minutes for QR scan...\n');

      // Wait for chat list to appear (after QR scan)
      await page.waitForSelector(chatListSelector, { timeout: 300000 });
      console.log('[2] Logged in successfully!');
    } else {
      console.log('[2] Session active — already logged in!');
    }

    await page.waitForTimeout(2000);
    await snap(page, 'wa_s1_logged_in');

    // ── Step 3: Open new chat to the target number ────────────────────────
    console.log('[3] Opening chat with +' + TO_NUMBER + '...');
    const chatUrl = `https://web.whatsapp.com/send?phone=${TO_NUMBER}&text=${encodeURIComponent(MESSAGE)}`;
    await page.goto(chatUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    await snap(page, 'wa_s2_chat_opening');

    // ── Step 4: Wait for compose box ─────────────────────────────────────
    console.log('[4] Waiting for compose box...');
    const inputSelector = 'footer [contenteditable="true"], [data-testid="conversation-compose-box-input"], p.selectable-text';
    await page.waitForSelector(inputSelector, { timeout: 60000 });
    await snap(page, 'wa_s3_compose_ready');

    // ── Step 5: Click input and send ─────────────────────────────────────
    console.log('[5] Clicking send button...');
    // The message is already pre-filled via URL; just press Enter
    const sendBtn = await page.$('[data-testid="send"], [aria-label="Send"], button[aria-label*="Send"]');
    if (sendBtn) {
      await sendBtn.click();
    } else {
      // Fallback: click the input and press Enter
      const input = await page.$(inputSelector);
      await input.click();
      await page.keyboard.press('Enter');
    }

    await page.waitForTimeout(4000);
    await snap(page, 'wa_s4_sent');

    console.log(`\n✓ WhatsApp message sent to +${TO_NUMBER}: "${MESSAGE}"`);

  } catch (err) {
    console.error('\nERROR:', err.message);
    await snap(page, 'wa_error');
    await context.close();
    process.exit(1);
  }

  await page.waitForTimeout(3000);
  await context.close();
})();
