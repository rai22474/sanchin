# Scenarios

[README](../../README.md) · [Docs](../index.md) · [Artifacts](index.md)

Executable acceptance scenarios, Gherkin by default (the adapter names the
runner). Feature files are organized by capability and are the living spec.
The product owner writes them when refining a story, tagged `@pending`; the
developer makes them red, then green, and drops the tag when the story
closes.

```gherkin
Feature: export

  # ST-12: AC 1, 2
  @pending
  Scenario: export includes archived items
    Given …
```

| Rule | Enforced by |
|---|---|
| Each scenario covering a criterion carries the trace comment above it; a trace comment not above a scenario is an error. | validator |
| Every feature file parses as Gherkin. | validator |
| A scenario whose stories are all unimplemented is tagged `@pending` (on itself, its rule or its feature); one covering an implemented story isn't. The runner skips the tag. | validator |
| Red for the right reason before the code exists. | developer, review |
