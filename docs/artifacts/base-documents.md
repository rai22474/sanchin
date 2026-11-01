# Project base documents

[README](../../README.md) · [Docs](../index.md) · [Artifacts](index.md)

Every project keeps four documents the skills read instead of holding
principles of their own. The adapter says where each one is; `/sanchin:init`
creates the missing ones and grills their content with the user.

| Document | Says | Read by |
|---|---|---|
| Mission and vision | Why the product exists, where it is going, the design principles it names. Optionally one vision per component. | product-owner, architect |
| Stack | Languages, frameworks, test runners, external services. | developer, reviewer, init (to propose gates) |
| Constitution | Decision records, standards and design smells: the rules code must follow. Its files feed the plan's constitution checklist. | architect, developer, reviewer |
| Glossary | Domain terms and the synonyms to avoid. | every skill, to name things the way the project does |

*Why separate documents:* each has one reader and one reason to change. A
single free-form "context" field mixes them and goes stale as a block.
