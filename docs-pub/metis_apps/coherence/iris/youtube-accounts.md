# YouTube accounts and channel access

Which Google account can connect a YouTube channel to IRIS, and what to do when the channel you
want isn't on offer. Written for whoever is about to click **Connect YouTube**, and for the
person who owns the channel and has to grant them access.

This is the part of YouTube setup that most often goes wrong, and it goes wrong in a way that
looks like a bug in METIS rather than a permissions problem: someone who uploads to the channel
by hand every week clicks Connect, and the channel simply isn't there.

For the Google Cloud project and the Connect click-path, see
[YouTube setup](youtube-setup.md). This page is only about **accounts and permissions**.

---

## The one rule

> **Only an _Owner_ of a channel can authorise API access to it.** People given YouTube Studio
> "channel permissions" of Manager, Editor, Viewer and so on can upload and edit on the YouTube
> website, but **their access is invisible to OAuth and the YouTube Data API** — which is
> exactly what IRIS uses. Being able to upload a video by hand in YouTube Studio does **not**
> mean you can connect that channel here.

Everything else on this page follows from that one sentence. If you remember nothing else:
**the person clicking Connect must own the channel, not merely have been invited to help run
it.**

There is also no way around it with a key or a service account. YouTube does not accept service
accounts for channel uploads at all — only credentials a real owner authorised in a browser.
That is why there is a Connect button rather than a field to paste a secret into.

---

## Which kind of channel do you have?

YouTube has two shapes of channel, and they behave differently here.

| | **Personal channel** | **Brand Account / organisation channel** |
|---|---|---|
| Tied to | One Google login, 1:1 | No login of its own — Google accounts are granted roles on it |
| Typically named | After a person | After an organisation or show |
| Signing in "as the channel" | Same as signing into that Google account | Not possible — there is no password for it |
| At Connect time | Often no picker appears | A picker appears, listing the personal channel *and* the Brand Account |

To check which you have: sign in at [youtube.com](https://www.youtube.com) and open the account
menu. If **Switch account** lists more than one channel, at least one of them is a Brand
Account.

---

## Case A — a personal channel

The channel is tied 1:1 to a single Google login: a channel named after a person, on that
person's own Google account. This is the simple case.

1. Sign in to that Google account during the Connect flow.
2. If that account has only the one channel, Google connects it directly — **no picker appears,
   because there is nothing to choose between.** This is normal, not a failure.
3. Confirm the channel name shown next to **Connected** afterwards.

---

## Case B — a Brand Account / organisation channel

A Brand Account is an organisation-shaped identity that **owns** a channel but is not itself a
login — there is no email and password for "The Coherence Company". Ordinary Google accounts are
granted roles on it instead. The channel exists even though nobody logs in *as* the channel.

1. The person doing the Connect must be signed in to a Google account that is an **Owner** of
   the channel — not merely a Studio-invited Manager or Editor. See [the one rule](#the-one-rule).
2. During consent an account picker appears. **Choose the organisation channel, not the personal
   one** — an account that owns a Brand Account sees both listed, and the personal one is often
   first.
3. Confirm the channel name shown next to **Connected** afterwards. If it shows the personal
   channel, the wrong entry was picked, or the account lacks Owner access — click **Reconnect**
   and try again.

IRIS deliberately asks Google for a fresh account picker every time (`prompt=consent
select_account`). Without that, someone who manages a Brand Account channel gets silently
defaulted to their personal channel with no way to choose. If you see no picker at all on an
account that definitely has several channels, something is wrong — don't assume the right one
was chosen.

---

## Granting Owner access

If the organisation channel doesn't appear in the picker, or connecting "succeeds" but lands on
the personal channel, the signed-in account almost certainly has only Studio-level
(Manager/Editor) access, which the API cannot see. An existing owner has to grant genuine
**Owner** access first.

Two different systems, depending on the channel's vintage — use whichever the channel actually
has:

- **Channel still on a legacy Brand Account** — an existing owner adds the account as an owner
  at [myaccount.google.com/brandaccounts](https://myaccount.google.com/brandaccounts) → the
  Brand Account → **Manage permissions**.
- **Channel migrated to YouTube Studio Channel Permissions** — an existing owner assigns the
  **Owner** role at **YouTube Studio → Settings → Permissions**. Google has been migrating
  channels off Brand-Account roles onto this system since 2024, and newer channels only have
  this path.

Then click **Connect YouTube** again. Owner access can take a little while to propagate — if the
channel still isn't offered straight away, wait a few minutes and retry before assuming it
failed.

> **A channel can have more than one owner**, so granting Owner access to the person doing the
> setup doesn't cost the original owner anything. That is usually the cleanest fix: grant
> ownership to the account that will run the connection, rather than passing a password around.

---

## Always confirm which channel you connected

On a successful connect, IRIS resolves and stores the channel's name and shows it next to
**Connected** in the step editor and on the conversation's step inspector.

**That display is the source of truth for where uploads will go.** It is the only way to tell a
correct connection from a plausible-looking wrong one — a personal channel authorised by mistake
connects perfectly happily, and nothing looks wrong until an episode lands on the wrong channel.
Check it every time, and especially after any Reconnect.

---

## Why this is so confusing

Three separate systems that grew up in different eras all pretend to be one:

1. The underlying **ownership** of the channel or Brand Account.
2. **YouTube Studio access** — the Manager/Editor invitations.
3. The **OAuth/API identity** Google resolves for a connecting app.

Studio permissions were layered on later, and the older API identity model does not honour them.
That is the whole reason someone can upload a video by hand yet be unable to connect the same
channel to IRIS — and why the failure is silent rather than an error message saying "you are
only an Editor". The only permission that satisfies the API is genuine **Owner** access.

---

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| The organisation channel doesn't appear in the picker | The signed-in account only has Studio Manager/Editor access, which the API cannot see | Have an existing owner grant genuine **Owner** access, then reconnect |
| No account picker appeared at all | That Google account has exactly one channel — there was nothing to choose | Normal. Confirm the channel name shown afterwards |
| Connected, but the wrong channel name is shown | The personal channel was picked instead of the organisation one, or the account lacks Owner access | Click **Reconnect** and pick carefully |
| Connecting "succeeds" but always lands on the personal channel | Studio-level access only — Google falls back to the channel the account genuinely owns | Grant Owner access on the organisation channel, then reconnect |
| Granted Owner access, channel still not offered | Propagation delay | Wait a few minutes and click **Connect YouTube** again |
| Google "did not return a refresh token" | A stale prior authorisation on that Google account | Revoke the app at [myaccount.google.com/permissions](https://myaccount.google.com/permissions), then Connect again |
| Uploads worked, then stopped about a week later | Not an account problem — the Google Cloud app is still in **Testing** mode, which expires tokens after 7 days | Ask a METIS admin to publish the app to Production |
| Error: connection expired or revoked | Access was revoked, or the owner changed their Google password | Reconnect on the journey step |

---

## Related pages

- **[YouTube setup](youtube-setup.md)** — the Google Cloud project, the OAuth client, and the
  Connect click-path.
- **[YouTube publishing](steps/youtube-uploader.md)** — what the upload, sync and promote steps
  actually do.
