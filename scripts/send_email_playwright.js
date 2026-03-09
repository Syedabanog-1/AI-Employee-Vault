/**
 * Send an email using Playwright via Gmail web UI.
 * Uses a persistent Chrome profile so login is only needed once.
 */

const { chromium } = require('playwright');
const path = require('path');
const fs   = require('fs');

const TO_EMAIL = 'faran.bsce40@iiu.edu.pk';
const SUBJECT  = 'Just Hello';
const BODY     = 'Hi there!';

const CHROME_EXE  = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PROFILE_DIR = path.join(__dirname, 'chrome-gmail-profile');

async function snap(page, name) {
  const p = path.join(__dirname, `${name}.png`);
  await page.screenshot({ path: p });
  console.log('  Screenshot:', p);
}

(async () => {
  fs.mkdirSync(PROFILE_DIR, { recursive: true });
  console.log('[0] Launching Chrome with persistent Gmail profile...');

  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    executablePath: CHROME_EXE,
    headless: false,
    slowMo: 80,
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
    // ── Step 1: Navigate to Gmail ──────────────────────────────────────────
    console.log('[1] Navigating to Gmail...');
    await page.goto('https://mail.google.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);

    // ── Step 2: Handle login if needed ────────────────────────────────────
    if (page.url().includes('accounts.google.com')) {
      console.log('\n>>> NOT LOGGED IN — A Chrome window has opened on your screen.');
      console.log('>>> 1. Click on the Chrome window in your taskbar');
      console.log('>>> 2. Log in to your Google / Gmail account');
      console.log('>>> Waiting up to 5 minutes...\n');
      await page.waitForURL('**/mail.google.com/**', { timeout: 300000 });
      console.log('[2] Login complete!');
    } else {
      console.log('[1] Already logged in to Gmail!');
    }

    await snap(page, 'gmail_s1_inbox');

    // ── Step 3: Click Compose ─────────────────────────────────────────────
    console.log('[3] Clicking Compose...');
    // Wait for Gmail to be fully loaded
    await page.waitForSelector('[gh="cm"], [data-tooltip="Compose"], [aria-label="Compose"]', { timeout: 20000 });
    await page.click('[gh="cm"], [data-tooltip="Compose"], [aria-label="Compose"]');
    // Wait for compose window to appear
    await page.waitForSelector('[aria-label="To"], [aria-label="To recipients"]', { timeout: 15000 });
    await snap(page, 'gmail_s2_compose');

    // ── Step 4: Fill To field ─────────────────────────────────────────────
    console.log('[4] Filling To field...');
    const toField = await page.$('[aria-label="To"], [aria-label="To recipients"]');
    await toField.click();
    await toField.type(TO_EMAIL, { delay: 30 });
    await page.keyboard.press('Tab');
    await page.waitForTimeout(500);

    // ── Step 5: Fill Subject field ────────────────────────────────────────
    console.log('[5] Filling Subject...');
    const subjectField = await page.waitForSelector('[aria-label="Subject"], [name="subjectbox"]', { timeout: 10000 });
    await subjectField.click();
    await subjectField.type(SUBJECT, { delay: 30 });

    // ── Step 6: Fill Body ─────────────────────────────────────────────────
    console.log('[6] Filling Body...');
    const bodyField = await page.waitForSelector('div[aria-label="Message Body"][contenteditable="true"]', { timeout: 10000 });
    await bodyField.click();
    await bodyField.type(BODY, { delay: 30 });
    await page.waitForTimeout(1000);
    await snap(page, 'gmail_s3_filled');

    // ── Step 7: Send ──────────────────────────────────────────────────────
    console.log('[7] Sending email...');
    // Use keyboard shortcut Ctrl+Enter as the most reliable way
    await page.keyboard.press('Control+Enter');
    await page.waitForTimeout(4000);
    await snap(page, 'gmail_s4_sent');

    console.log(`\n✓ Email sent to ${TO_EMAIL}!`);
    console.log(`  Subject: ${SUBJECT}`);
    console.log(`  Body:    ${BODY}`);

  } catch (err) {
    console.error('\nERROR:', err.message);
    await snap(page, 'gmail_error');
    process.exit(1);
  } finally {
    await page.waitForTimeout(3000);
    await context.close();
  }
})();
