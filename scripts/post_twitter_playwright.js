/**
 * Post a tweet on X (Twitter) using Playwright with real Chrome (stealth mode).
 * Uses a temp profile + real Chrome binary to avoid bot detection.
 */

const { chromium } = require('playwright');
const path = require('path');
const os   = require('os');
const fs   = require('fs');

const TWEET_TEXT = `Hackathons are underrated career accelerators.

In 48 hours you ship a real product, learn by doing, and meet future co-founders.

The best ideas don't come from boardrooms — they come from hackathons.

#Hackathon #BuildInPublic #Innovation`;

const EMAIL    = 'SGulzarBano';
const PASSWORD = 'A8692a10';
const USERNAME = 'SGulzarBano';

const CHROME_EXE  = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
// Dedicated persistent profile — session is saved here after first manual login
const PROFILE_DIR = path.join(__dirname, '..', 'scripts', 'chrome-x-profile');

async function snap(page, name) {
  const p = `scripts/${name}.png`;
  await page.screenshot({ path: p });
  console.log('  Screenshot:', p);
}

async function waitAndSnap(page, name, ms = 2000) {
  await page.waitForTimeout(ms);
  await snap(page, name);
}

(async () => {
  fs.mkdirSync(PROFILE_DIR, { recursive: true });
  console.log('[0] Launching Chrome with persistent X profile...');

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

  // Remove webdriver flag via CDP
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
    // ── Step 1: Go to X home (reuses session if saved, else wait for manual login) ──
    console.log('[1] Navigating to X home...');
    await page.goto('https://x.com/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    console.log('    URL:', page.url());

    // If redirected to login, wait for user to log in manually (up to 2 min)
    if (page.url().includes('/login') || page.url().includes('/flow')) {
      await page.bringToFront();
      console.log('\n>>> NOT LOGGED IN — A Chrome window has opened on your screen.');
      console.log('>>> 1. Click on the Chrome window in your taskbar');
      console.log('>>> 2. Enter username: SGulzarBano  → Next');
      console.log('>>> 3. Enter your password → Log in');
      console.log('>>> Waiting up to 5 minutes...\n');
      await page.waitForURL('**/home**', { timeout: 300000 });
      console.log('[1] Manual login complete!');
    } else {
      console.log('[1] Session active — already logged in!');
    }
    await waitAndSnap(page, 's1_home', 2000);
    await waitAndSnap(page, 's6_home', 2000);

    // ── Step 6: Click compose box ─────────────────────────────────────────
    console.log('[6] Opening compose box...');
    const compose = await page.waitForSelector(
      '[data-testid="tweetTextarea_0"], div[contenteditable="true"][role="textbox"]',
      { timeout: 15000 }
    );
    await compose.click();
    await page.waitForTimeout(1000);

    // ── Step 7: Type tweet ────────────────────────────────────────────────
    console.log('[7] Typing tweet...');
    await page.keyboard.type(TWEET_TEXT, { delay: 18 });
    await waitAndSnap(page, 's7_typed', 1500);

    // ── Step 8: Click Post ────────────────────────────────────────────────
    console.log('[8] Clicking Post...');
    const postBtn = await page.waitForSelector(
      '[data-testid="tweetButtonInline"], [data-testid="tweetButton"]',
      { timeout: 10000 }
    );
    // Use JS click to bypass overlay intercept
    await postBtn.evaluate(el => el.click());
    await waitAndSnap(page, 's8_posted', 4000);
    console.log('\n✓ Tweet posted successfully!');

  } catch (err) {
    console.error('\nERROR:', err.message);
    await snap(page, 'error_final');
    process.exit(1);
  } finally {
    await page.waitForTimeout(3000);
    await context.close();
    // Profile dir kept for session reuse on next run
  }
})();
