# Access & Permissions, from a User's View

This answers the everyday questions — "why can't I see X?", "why can't I edit this?", "how do
I get access?" — without needing the permission model internals. For the full model (groups,
config flags, the capability rules), see [Permissions](PERMISSIONS.md).

---

## Why a nav group or app isn't showing

A whole app's nav group (Coherence, Gathering, Audax, Outreach) can be missing for two very
different reasons — it's worth telling them apart:

1. **You don't have access to that app.** Access to some apps is granted by membership of a
   dedicated group (for example, Coherence access requires the `coherence_users` group).
   Being staff or a broad editor does **not** automatically grant these — they're a
   deliberate opt-in.
2. **Your current Focus has none of those records.** Even with access, an app's nav group
   only appears when your current Focus actually has the relevant records. Switch Focus (or
   go to "All") and it may appear. This is *scope*, not permission — see
   [Focus](../web/app/focus-and-scoping.md).

If switching Focus doesn't bring it back, it's an access matter, not scope.

## The `*_users` group pattern

Several capabilities are gated by a named group whose name ends in `_users` (e.g.
`coherence_users`). If you need access to one of these areas, the fix is usually "be added to
the right group" — ask an administrator (someone with broad edit / staff rights) to add you.

## "Can't see it" vs. "can see it but can't act"

These are different limits:

- **Can't see the nav item / section at all** — an access or scope issue (above).
- **Can see it but can't create/edit/delete** — you have *view* access but not the *action*
  right. Many actions (creating holons, managing teams, editing relationships, managing
  journeys) require broad edit access; viewing the same records may not. So seeing something
  you can't change is expected, not a glitch.

A useful rule of thumb from the model: **editing** a holon is possible either with broad edit
rights or by being an active team member of that holon (or one of its parents); **deleting**
is narrower (staff only); **creating** and **team management** generally need broad edit
rights. The full breakdown is in [Permissions → What each role can do](PERMISSIONS.md#what-each-role-can-do).

## Checking or requesting your own access

- **Settings** shows the cards and tools available to you; what's present there reflects your
  access.
- To change your access — join a group, get broad edit rights, get Coherence/Audax/etc.
  access — contact an administrator. Access is granted through Django groups and rights that
  only admins can set.
