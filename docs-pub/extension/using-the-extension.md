# Using the Chrome Extension

The METIS Chrome extension lets you look up and add LinkedIn profiles and companies straight
into METIS without leaving LinkedIn, and gives you a contextual side panel on METIS CRM
pages.

> This is the usage guide. The extension's internals and API are covered separately in the
> developer docs; you don't need those to use it.

---

## Installing it

The extension is distributed through METIS itself — the **Settings** page has a Chrome
extension download card (visible to users with broad edit rights). Download it from there and
load it in Chrome, then pin it so its icon is visible in the toolbar. If you don't see the
download card, ask an administrator.

## Signing in / the handshake with METIS

The extension uses your existing METIS login in the same browser — there's no separate
password. When you're logged into METIS in that browser, the extension detects the web app
and connects automatically (a handshake between the page and the extension).

- **Connected** — the extension recognises your METIS session and can add records and show
  the side panel.
- **Disconnected** — if it shows disconnected, open METIS and make sure you're logged in in
  the same browser, then reload the LinkedIn tab or the extension.

## Using it on LinkedIn

On `linkedin.com`, the extension detects what kind of page you're on and reads the relevant
context:

- **Profile pages** — a person's LinkedIn profile.
- **Company pages** — an organisation.
- **Messaging threads** — the person you're in a conversation with.

From there you can **add the detected person or company into METIS** (or look them up if
they already exist), so you can capture someone straight from LinkedIn instead of copying
details across by hand.

## The side panel on METIS pages

On METIS CRM pages, the extension provides a **side panel** with contextual information and
actions for what you're looking at. Open it from the extension's toolbar icon while on a
METIS page.

## Common issues

- **It's not detecting a LinkedIn page** — make sure you're on a supported page type (profile,
  company, or messaging thread) and that the page has finished loading; reload if needed.
- **The side panel won't load** — confirm you're on a METIS page and signed in; a
  disconnected session is the usual cause (see *Signing in* above).
- **Shows disconnected** — log into METIS in the same browser and reload.
