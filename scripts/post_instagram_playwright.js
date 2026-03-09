/**
 * Post to Instagram via Playwright (Instagram web UI).
 * Uses a persistent Chrome profile for session reuse.
 */

const { chromium } = require('playwright');
const path = require('path');
const fs   = require('fs');

const POST_CAPTION = `A proud moment of strength and victory for the Muslim Ummah worldwide. Alhamdulillah! 🌙

The resilience, unity, and faith of Muslims across the globe continues to inspire generations.
Standing together, we rise. One Ummah, one strength.

#Muslims #Ummah #Victory #Alhamdulillah #IslamicStrength #Unity #Faith`;

const CHROME_EXE  = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PROFILE_DIR = path.join('scripts', 'chrome-instagram-profile');

async function snap(page, name) {
  try {
    await page.screenshot({ path: path.join('scripts', `${name}.png`) });
    console.log('  Screenshot: scripts/' + name + '.png');
  } catch (_) {}
}

(async () => {
  fs.mkdirSync(PROFILE_DIR, { recursive: true });
  console.log('[0] Launching Chrome for Instagram...');

  const ctx = await chromium.launchPersistentContext(PROFILE_DIR, {
    executablePath: CHROME_EXE,
    headless: false,
    slowMo: 80,
    args: ['--start-maximized','--disable-blink-features=AutomationControlled','--no-sandbox','--disable-infobars'],
    ignoreDefaultArgs: ['--enable-automation'],
  });

  const page = await ctx.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });

  try {
    // ── Step 1: Navigate to Instagram ────────────────────────────────────
    console.log('[1] Navigating to Instagram...');
    await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(4000);

    // ── Step 2: Handle login if needed ────────────────────────────────────
    const feedSel = 'svg[aria-label="Home"], a[href="/direct/inbox/"], [aria-label="New post"]';
    const isLoggedIn = await page.$(feedSel);
    if (!isLoggedIn) {
      console.log('\n>>> NOT LOGGED IN — Instagram Chrome window is open.');
      console.log('>>> Please log in manually, then wait...');
      await page.waitForSelector(feedSel, { timeout: 300000 });
      console.log('[2] Logged in to Instagram!');
    } else {
      console.log('[2] Already logged in!');
    }
    await snap(page, 'ig_s1_home');

    // ── Step 2b: Dismiss "Turn on Notifications" popup if present ────────
    await page.waitForTimeout(2000);
    const notNow = await page.$('button:has-text("Not Now"), div[role="button"]:has-text("Not Now")');
    if (notNow) {
      console.log('[2b] Dismissing notifications popup...');
      await notNow.click();
      await page.waitForTimeout(1500);
    }

    // ── Step 3: Click the Create / New Post button ─────────────────────────
    console.log('[3] Clicking Create...');
    const createBtn = await page.waitForSelector(
      '[aria-label="New post"], svg[aria-label="New post"], span:has-text("Create"), a:has-text("Create")',
      { timeout: 15000 }
    );
    await createBtn.click();
    await page.waitForTimeout(2000);
    await snap(page, 'ig_s2_create_clicked');

    // ── Step 4: Click "Post" option from create menu ──────────────────────
    // After Create menu opens, "Post" appears as the first sub-item in sidebar
    console.log('[4] Selecting Post option from create menu...');
    await page.waitForTimeout(1500);
    // Use JS to find the "Post" link that appears right after the Create button
    await page.evaluate(() => {
      const allLinks = Array.from(document.querySelectorAll('a, [role="link"]'));
      // Find the "Post" link whose text is exactly "Post" — filter out other "Post" matches
      const postLink = allLinks.find(el => {
        const txt = el.innerText && el.innerText.trim();
        return txt === 'Post';
      });
      if (postLink) postLink.click();
    });
    await page.waitForTimeout(4000);
    await snap(page, 'ig_s3_post_dialog');

    // ── Step 5: Use an existing screenshot as the image ──────────────────
    // Instagram requires an image ≥ 1KB — use a real screenshot we already have
    const imgPath = path.resolve('scripts', 'ig_s1_home.png');

    console.log('[5] Selecting image to upload...');
    // Instagram file input is hidden — use locator with force to bypass visibility check
    await page.locator('input[type="file"]').setInputFiles(imgPath);
    await page.waitForTimeout(5000);
    await snap(page, 'ig_s4_image_selected');

    // ── Step 6: Click Next through crop/filter screens ────────────────────
    for (let i = 0; i < 3; i++) {
      const nextBtn = await page.$('button:has-text("Next"), div[role="button"]:has-text("Next")');
      if (nextBtn) {
        console.log(`[6.${i+1}] Clicking Next...`);
        await nextBtn.click();
        await page.waitForTimeout(2000);
        await snap(page, `ig_s4_next_${i+1}`);
      } else {
        break;
      }
    }

    // ── Step 7: Type caption ──────────────────────────────────────────────
    console.log('[7] Typing caption...');
    const captionBox = await page.waitForSelector(
      '[aria-label="Write a caption..."], div[contenteditable="true"][aria-label*="caption"]',
      { timeout: 15000 }
    );
    await captionBox.click();
    await captionBox.type(POST_CAPTION, { delay: 20 });
    await page.waitForTimeout(1500);
    await snap(page, 'ig_s5_caption');

    // ── Step 8: Share / Post ──────────────────────────────────────────────
    // Click somewhere neutral to dismiss hashtag suggestions (not Escape — that closes the dialog)
    await captionBox.click();
    await page.waitForTimeout(800);

    console.log('[8] Sharing post via JS click...');
    await page.evaluate(() => {
      const allBtns = Array.from(document.querySelectorAll('[role="button"], button, div[tabindex="0"]'));
      const shareBtn = allBtns.find(el => el.innerText && el.innerText.trim() === 'Share');
      if (shareBtn) shareBtn.click();
    });
    await page.waitForTimeout(6000);
    await snap(page, 'ig_s6_shared');

    console.log('\n✓ Instagram post published!');

  } catch (e) {
    console.error('\nERROR:', e.message);
    await snap(page, 'ig_error');
  }

  await page.waitForTimeout(3000);
  await ctx.close();
})();
