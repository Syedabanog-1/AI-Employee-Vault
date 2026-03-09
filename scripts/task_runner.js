/**
 * Multi-task runner:
 * 1. WhatsApp to +923122726480 — "kaise ho Shagufta"
 * 2. Facebook post — new supreme leader of Iran
 * 3. Email to gulzar_bano@yahoo.com
 *
 * Run: node scripts/task_runner.js [whatsapp|facebook|email]
 */

const { chromium } = require('playwright');
const path = require('path');
const fs   = require('fs');

const CHROME_EXE = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

async function snap(page, name) {
  try {
    await page.screenshot({ path: path.join('scripts', `${name}.png`) });
    console.log('  Screenshot: scripts/' + name + '.png');
  } catch (_) {}
}

// ─────────────────────────────────────────────────────────────────
// TASK 1: WhatsApp
// ─────────────────────────────────────────────────────────────────
async function sendWhatsApp() {
  const TO_NUMBER = '923122726480';
  const MESSAGE   = 'kaise ho Shagufta';
  const PROFILE   = path.join('scripts', 'chrome-whatsapp-profile');

  fs.mkdirSync(PROFILE, { recursive: true });
  console.log('\n═══ WHATSAPP ═══');

  const ctx = await chromium.launchPersistentContext(PROFILE, {
    executablePath: CHROME_EXE,
    headless: false, slowMo: 60,
    args: ['--start-maximized','--disable-blink-features=AutomationControlled','--no-sandbox','--disable-infobars'],
    ignoreDefaultArgs: ['--enable-automation'],
  });
  const page = await ctx.newPage();
  await page.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); });

  try {
    const url = `https://web.whatsapp.com/send?phone=${TO_NUMBER}&text=${encodeURIComponent(MESSAGE)}`;
    console.log('[1] Navigating to chat with +' + TO_NUMBER);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(4000);

    console.log('[2] Waiting for compose box...');
    const inputSel = 'footer [contenteditable="true"], [data-testid="conversation-compose-box-input"], p.selectable-text';
    await page.waitForSelector(inputSel, { timeout: 60000 });

    console.log('[3] Sending...');
    const sendBtn = await page.$('[data-testid="send"], button[aria-label="Send"]');
    if (sendBtn) {
      await sendBtn.click();
    } else {
      const inp = await page.$(inputSel);
      await inp.click();
      await page.keyboard.press('Enter');
    }
    await page.waitForTimeout(4000);
    await snap(page, 'wa_shagufta_sent');
    console.log('✓ WhatsApp sent to +' + TO_NUMBER + ': "' + MESSAGE + '"');
  } catch (e) {
    console.error('WhatsApp ERROR:', e.message);
    await snap(page, 'wa_shagufta_error');
  }
  await ctx.close();
}

// ─────────────────────────────────────────────────────────────────
// TASK 2: Facebook post
// ─────────────────────────────────────────────────────────────────
async function postFacebook() {
  const POST_TEXT = `Breaking: Iran's New Supreme Leader Takes Office

Following the passing of Ayatollah Khamenei, Iran has appointed a new Supreme Leader, marking a historic turning point for the Islamic Republic. The new leader is expected to continue Iran's path of independence and sovereignty.

This transition signals a new chapter for Iran and the wider Muslim world. The international community watches closely as the new leadership takes shape.

#Iran #SupremeLeader #IslamicRepublic #BreakingNews`;

  const PROFILE = path.join('scripts', 'chrome-facebook-profile');
  fs.mkdirSync(PROFILE, { recursive: true });
  console.log('\n═══ FACEBOOK ═══');

  const ctx = await chromium.launchPersistentContext(PROFILE, {
    executablePath: CHROME_EXE,
    headless: false, slowMo: 80,
    args: ['--start-maximized','--disable-blink-features=AutomationControlled','--no-sandbox','--disable-infobars'],
    ignoreDefaultArgs: ['--enable-automation'],
  });
  const page = await ctx.newPage();
  await page.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); });

  try {
    console.log('[1] Navigating to Facebook...');
    await page.goto('https://www.facebook.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(4000);

    // Detect login page: look for the compose feed; if absent, need login
    const feedSel = '[role="feed"], [data-pagelet="FeedUnit_0"], [aria-label="Create a post"]';
    const isLoggedIn = await page.$(feedSel);
    if (!isLoggedIn) {
      console.log('\n>>> NOT LOGGED IN — Facebook Chrome window has opened.');
      console.log('>>> Please log in manually in the Chrome window.');
      console.log('>>> Waiting up to 5 minutes...\n');
      await page.waitForSelector(feedSel, { timeout: 300000 });
      console.log('[1] Logged in to Facebook!');
    } else {
      console.log('[1] Already logged in to Facebook!');
    }
    await snap(page, 'fb_iran_s1_home');

    console.log('[2] Clicking "What\'s on your mind?"...');
    // Click the compose placeholder text
    const composeBox = await page.waitForSelector(
      '[aria-label="Create a post"], [data-testid="status-attachment-mentions-input"]',
      { timeout: 20000 }
    );
    await composeBox.click();
    await page.waitForTimeout(2000);

    console.log('[3] Typing post...');
    await page.keyboard.type(POST_TEXT, { delay: 15 });
    await page.waitForTimeout(1500);
    await snap(page, 'fb_iran_s2_typed');

    // Dismiss any hashtag/mention autocomplete dropdown
    await page.keyboard.press('Escape');
    await page.waitForTimeout(800);

    console.log('[4] Submitting post via JavaScript click...');
    // Use JS to find and click the Post/Next button by its text
    const clicked = await page.evaluate(() => {
      const allBtns = Array.from(document.querySelectorAll('[role="button"], button'));
      // Prefer "Post" over "Next"
      const postBtn = allBtns.find(el => el.textContent.trim() === 'Post');
      if (postBtn) { postBtn.click(); return 'post'; }
      const nextBtn = allBtns.find(el => el.textContent.trim() === 'Next');
      if (nextBtn) { nextBtn.click(); return 'next'; }
      return null;
    });
    console.log('[4] Clicked:', clicked);
    await page.waitForTimeout(3000);

    // Check if we're on an intermediate screen (Life Update, Post Settings, etc.)
    // Keep clicking "Next" / "Post" until we've actually published
    for (let attempt = 0; attempt < 5; attempt++) {
      const isSettingsScreen = await page.$('div:has-text("Post settings"), div:has-text("Create life update")');
      if (!isSettingsScreen) break;

      console.log(`[4-step${attempt+1}] Intermediate screen — clicking Post...`);
      const didClick = await page.evaluate(() => {
        const allBtns = Array.from(document.querySelectorAll('[role="button"], button'));
        const postBtn = allBtns.find(el => el.textContent.trim() === 'Post');
        if (postBtn) { postBtn.click(); return true; }
        return false;
      });
      await page.waitForTimeout(3000);
      if (!didClick) break;
    }
    await page.waitForTimeout(5000);
    await snap(page, 'fb_iran_s3_posted');
    console.log('✓ Facebook post published!');
  } catch (e) {
    console.error('Facebook ERROR:', e.message);
    await snap(page, 'fb_iran_error');
  }
  await ctx.close();
}

// ─────────────────────────────────────────────────────────────────
// TASK 3: Email via Gmail
// ─────────────────────────────────────────────────────────────────
async function sendEmail() {
  const TO_EMAIL = 'gulzar_bano@yahoo.com';
  const SUBJECT  = 'Good News for Muslims';
  const BODY = `Alhamdulillah, the Muslim Ummah continues to show remarkable strength and unity across the globe.
From the steadfast resilience of believers in times of hardship to the growing influence of Islamic scholarship, Muslims worldwide stand firm in their faith.
The youth of the Ummah are rising with knowledge, technology, and a renewed sense of purpose and identity.
Economic, political, and spiritual empowerment among Muslim communities is accelerating at an unprecedented pace.
Indeed, with Allah's blessings and the unity of the Ummah, the strength of Muslims grows stronger with each passing day. Ameen.`;

  const PROFILE = path.join('scripts', 'chrome-gmail-profile');
  fs.mkdirSync(PROFILE, { recursive: true });
  console.log('\n═══ EMAIL ═══');

  const ctx = await chromium.launchPersistentContext(PROFILE, {
    executablePath: CHROME_EXE,
    headless: false, slowMo: 80,
    args: ['--start-maximized','--disable-blink-features=AutomationControlled','--no-sandbox','--disable-infobars'],
    ignoreDefaultArgs: ['--enable-automation'],
  });
  const page = await ctx.newPage();
  await page.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); });

  try {
    console.log('[1] Navigating to Gmail...');
    await page.goto('https://mail.google.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);

    if (page.url().includes('accounts.google.com')) {
      console.log('\n>>> NOT LOGGED IN — log in to Gmail in the Chrome window');
      await page.waitForURL('**/mail.google.com/**', { timeout: 300000 });
    }
    console.log('[1] Gmail loaded');

    console.log('[2] Clicking Compose...');
    await page.waitForSelector('[gh="cm"], [data-tooltip="Compose"], [aria-label="Compose"]', { timeout: 20000 });
    await page.click('[gh="cm"], [data-tooltip="Compose"], [aria-label="Compose"]');
    await page.waitForSelector('[aria-label="To"], [aria-label="To recipients"]', { timeout: 15000 });
    await snap(page, 'email_iran_s1_compose');

    console.log('[3] Filling To...');
    const toField = await page.$('[aria-label="To"], [aria-label="To recipients"]');
    await toField.click();
    await toField.type(TO_EMAIL, { delay: 30 });
    await page.keyboard.press('Tab');
    await page.waitForTimeout(500);

    console.log('[4] Filling Subject...');
    const subj = await page.waitForSelector('[aria-label="Subject"], [name="subjectbox"]', { timeout: 10000 });
    await subj.click();
    await subj.type(SUBJECT, { delay: 30 });

    console.log('[5] Filling Body...');
    const body = await page.waitForSelector('div[aria-label="Message Body"][contenteditable="true"]', { timeout: 10000 });
    await body.click();
    await body.type(BODY, { delay: 20 });
    await page.waitForTimeout(1000);
    await snap(page, 'email_iran_s2_filled');

    console.log('[6] Sending...');
    await page.keyboard.press('Control+Enter');
    await page.waitForTimeout(4000);
    await snap(page, 'email_iran_s3_sent');
    console.log('✓ Email sent to ' + TO_EMAIL);
    console.log('  Subject: ' + SUBJECT);
  } catch (e) {
    console.error('Email ERROR:', e.message);
    await snap(page, 'email_iran_error');
  }
  await ctx.close();
}

// ─────────────────────────────────────────────────────────────────
// MAIN
// ─────────────────────────────────────────────────────────────────
(async () => {
  const task = process.argv[2];
  if (task === 'whatsapp') await sendWhatsApp();
  else if (task === 'facebook') await postFacebook();
  else if (task === 'email') await sendEmail();
  else {
    await sendWhatsApp();
    await postFacebook();
    await sendEmail();
  }
})();
