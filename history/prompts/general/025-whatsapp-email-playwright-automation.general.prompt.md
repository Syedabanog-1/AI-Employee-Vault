---
id: "025"
title: "WhatsApp and Email Playwright Automation"
stage: general
date: "2026-03-10"
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 1-bronze-phase
user: Syeda Gulzar Bano
command: "send whatsapp + email via playwright mcp"
labels: ["playwright", "whatsapp", "gmail", "automation", "browser"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - scripts/send_whatsapp_playwright.js
  - scripts/send_email_playwright.js
tests: []
---

## Prompt

playwright mcp server ko use kr k kise bhi whatsapp number par message and kise bhi email adress par email send kro subject Just Hello and body Hi there! again and again mujhey playwright mcp server ka reference na daina padey configure settings whatsapp number +923322236597 and email is faran.bsce40@iiu.edu.pk

## Response

Created two Playwright browser automation scripts:

1. `scripts/send_whatsapp_playwright.js` — opens WhatsApp Web via persistent Chrome profile, navigates to `web.whatsapp.com/send?phone=923322236597`, waits for compose box, and sends "Hi there!"
2. `scripts/send_email_playwright.js` — opens Gmail via persistent Chrome profile, clicks Compose, fills To/Subject/Body fields, sends with Ctrl+Enter

**Key fixes applied during development:**
- WhatsApp selector: added `#side` fallback for WhatsApp Business Web (different DOM than regular WhatsApp Web)
- Gmail body selector: changed to `div[aria-label="Message Body"][contenteditable="true"]` to avoid matching the hidden `<textarea>` that Gmail also renders with the same aria-label
- Chrome profiles saved under `scripts/chrome-whatsapp-profile/` and `scripts/chrome-gmail-profile/` for session reuse (no re-login needed on subsequent runs)

**Results confirmed via screenshots:**
- WhatsApp: "Hi there!" delivered to +923322236597 (Syeda Uzma Ahmed) at 12:53 am
- Email: Gmail "Message sent" toast confirmed delivery to faran.bsce40@iiu.edu.pk, subject "Just Hello", body "Hi there!"

## Outcome

✅ Both messages delivered successfully via Playwright browser automation using persistent Chrome profiles.
