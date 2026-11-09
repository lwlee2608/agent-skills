---
name: improve-ui-ux
description: Use when asked to improve, polish, or audit the UI, UX, or look of an existing app in the current repo. Asks what to improve and which pages, screenshots the running app, then applies the fixes the user picks.
user-invocable: true
---

# Improve UI/UX

Improve an existing app's interface without rewriting it. The user picks the focus and scope. The agent brings screenshots and suggestions.

## Rules

1. **Map the routes first.** Read the code. List the pages, framework, shared components, and design tokens. The scope question needs real page names.

2. **Ask focus and scope in one batch.** Use the question tool:
   - **Focus** (multi-select): UI, UX, aesthetic, or all.
     - UI: layout, components, states, accessibility.
     - UX: flows, navigation, feedback, friction.
     - Aesthetic: color, type, spacing, polish.
   - **Scope**: pages from rule 1. For example, the landing page, one page, or the whole app.

   Ask before inspecting. This avoids work on areas the user does not care about.

3. **Inspect the running app in a browser.** Launch the app. Use any browser automation tool you have (Claude in Chrome, Playwright, browser-use). Screenshot each page at desktop and mobile widths. Walk the main flows for UX. Some problems only show when rendered, like overflow, contrast, and dead clicks. If the app cannot run, say so and review the code.

4. **Ask follow-ups with suggestions.** Turn findings into questions. Give 2-4 options each, with your pick first. Cite the page and screenshot. Also ask taste questions the code cannot answer, like "keep this style or refresh it?"

5. **Reuse the design system.** Use existing components and tokens. Never hardcode a value the theme defines. Add new tokens or components only with user approval.

6. **Make one change per finding.** Then the user can reject one and keep the rest.

7. **Avoid the AI-generated look.** It reads as cheap, generic, and low effort. The goal is a design that looks premium and well thought out. Flag these in existing pages, and never add them:
   - Em dashes in copy. Use a period, comma, or colon.
   - Punctuation at the end of a hero title.
   - Buzzwords like "unlock", "elevate", "seamless", "supercharge".
   - Purple-blue gradients, glassmorphism, and glowing blobs.
   - Emoji as icons or bullets.
   - Pills everywhere: badges, tags, and buttons all rounded-full.
   - Every section as a centered grid of icon, title, and blurb cards.

   Prefer specific copy, real product screenshots, one accent color, and a clear visual hierarchy.

## Verification procedure

1. Re-screenshot each changed page at the same widths. Show before and after.
2. Run the repo's lint, type check, and tests.
