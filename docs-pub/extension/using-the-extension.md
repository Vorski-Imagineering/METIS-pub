# Using the Chrome Extension

The METIS Chrome extension lets you look up and add LinkedIn profiles and companies straight
into METIS without leaving LinkedIn, shows known people while you read Gmail, and gives you a
contextual side panel on METIS CRM and compatible application pages.

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

## Using it in Gmail

Open a message in `mail.google.com`, then open the METIS side panel. The extension reads the
visible From, To, and Cc addresses and looks for exact email matches among existing METIS
People. When several people match, use the **People on this email** selector to switch between
their full profiles.

The extension does not send the message subject, body, attachments, or labels to METIS. Gmail
support is read-only: an address that is not already in METIS is shown as unknown and is not
automatically imported.

## Compatible application pages

Applications maintained alongside METIS can declare the METIS People and Holons shown on a
page. The extension then displays a compact context list; selecting a person opens the same
full Person panel used elsewhere. Application developers should follow the page-context
contract documented in the METIS developer documentation rather than making the extension
scrape application-specific markup.

## Common issues

- **It's not detecting a LinkedIn page** — make sure you're on a supported page type (profile,
  company, or messaging thread) and that the page has finished loading; reload if needed.
- **It doesn't show Gmail participants** — open an individual message and wait for its header
  to finish loading. Only visible From, To, and Cc addresses are considered.
- **The side panel won't load** — confirm you're on a METIS page and signed in; a
  disconnected session is the usual cause (see *Signing in* above).
- **Shows disconnected** — log into METIS in the same browser and reload.
