---
name: slack-dm-summary
description: Summarize a Slack DM thread into a 3-bullet recap.
version: 1.0.0
author: AI Build Lab
license: MIT
---

# slack-dm-summary

Use this skill when a user asks you to summarize a Slack direct message
conversation. The output should be three bullet points covering: who said
what, what was decided, and what the open questions are.

## When to invoke

Triggered by phrases like:

- "summarize this DM"
- "give me the gist of this thread"
- "what did we decide in chat"

## How it works

1. Read the messages provided in the conversation context.
2. Identify the participants and group their messages by speaker.
3. Extract any decisions (look for action verbs and commitments).
4. List any unanswered questions (look for question marks without follow-up).
5. Format as three bullets, no more.

## Output template

```
- Who: <participants and the gist of their positions>
- Decided: <one-sentence outcome, or "no decision yet">
- Open: <one-sentence list of unresolved items, or "none">
```

## Example

Given a thread between Alice and Bob debating a launch date, the output is:

```
- Who: Alice wanted Friday, Bob wanted next Monday for QA buffer.
- Decided: Launch on Tuesday as a compromise.
- Open: Who owns the announcement post.
```

That is the entire skill. No tool calls, no shell, no network access.
