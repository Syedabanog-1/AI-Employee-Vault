---
id: "024"
title: "Twitter Post Playwright Success"
stage: general
date: 2026-03-09
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: SGulzarBano
command: "post to twitter using playwright"
labels: ["twitter", "playwright", "social-media", "automation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - scripts/post_twitter_playwright.js
  - scripts/chrome-x-profile/
tests: []
---

## Prompt

post to twitter i mean x my gmail id is banogulzar116@gmail.com use playwright to post to x
user name is SGulzarBano post about doing hackathon importance

## Response

Successfully posted to X (@SGulzarBano) using Playwright with persistent Chrome profile.

**Tweet posted:**
```
Hackathons are underrated career accelerators.

In 48 hours you ship a real product, learn by doing, and meet future co-founders.

The best ideas don't come from boardrooms — they come from hackathons.

#Hackathon #BuildInPublic #Innovation
```

**Key fixes applied:**
1. Switched from temp Chrome profile → persistent profile (`scripts/chrome-x-profile/`) to reuse login session
2. Manual login via Google SSO ("Sign in with Google") saved the session
3. Used `el.evaluate(el => el.click())` (JS click) to bypass X's `#layers` overlay intercepting the Post button click
4. Shortened tweet from ~320 chars to ~240 chars (under 280 limit)

**Outcome:** X confirmed "Your post was sent." — visible in `scripts/s8_posted.png`
