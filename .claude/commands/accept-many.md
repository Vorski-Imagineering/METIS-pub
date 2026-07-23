---
description: Accept multiple pending LinkedIn invitations serially, sending the message from texts/accept-invite.txt to each
allowed-tools: Read, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__find, mcp__claude-in-chrome__form_input, mcp__claude-in-chrome__read_page
---

Accept **$ARGUMENTS** pending LinkedIn connection invitations, one at a time, by running the `/accept-one` flow that many times serially.

## Steps

1. Parse `$ARGUMENTS` as an integer `N`. If it is missing, not a number, or less than 1, stop and tell the user: "Please provide a number, e.g. `/accept-many 5`."

2. Run the full `/accept-one` flow **N times**, one after the other. Do not start the next iteration until the current one has fully completed (message sent and confirmed).

3. **Wait between iterations.** Accepting invitations back-to-back is the clearest possible
   automation signature. Before each iteration after the first, pause:

   ```javascript
   const humanDelay = (meanMs, minMs, maxMs) => {
     // Shifted exponential. Do NOT clamp at the minimum instead: clamping puts ~30%
     // of draws on the exact same value, which is itself a machine fingerprint.
     const scale = Math.max(1, (meanMs - minMs) / 1.2);
     let d = minMs - scale * Math.log(1 - Math.random());
     if (Math.random() < 0.1) d += -scale * 2 * Math.log(1 - Math.random());  // distracted
     return Math.min(maxMs, Math.round(d));
   };
   await new Promise(r => setTimeout(r, humanDelay(30000, 12000, 180000)));  // 30 s mean
   ```

   After every 8–15 iterations (re-randomise the threshold), take a longer break of 2–10
   minutes: `humanDelay(300000, 120000, 600000)`. **Announce every long break before it
   starts**, with its length and the current position:

   ```
   [8/20] Taking a 5 min break to stay within LinkedIn's limits — resuming after.
   ```

   Do not announce the short 30-second waits between iterations; the `[{i}/{N}]` lines
   already show the run is alive.

   **Before the first iteration**, tell the user the run will take roughly `N × 30 s` plus
   breaks, so a large N is understood to be a long-running job rather than something that
   finishes immediately. See the **Pacing** section of
   `.claude/skills/linkedin-automation/SKILL.md` for the rationale.

4. Keep a running count. After each successful iteration print: `[{i}/{N}] Message sent to **{name}**.`

5. If any iteration fails at any step, stop immediately and report the exact error and which iteration it failed on (e.g. "Failed on iteration 2/5: accept button not found"). Do not continue to the next iteration.

6. When all N iterations are done, print a final summary: `Done — sent messages to N connections: {name1}, {name2}, …`
