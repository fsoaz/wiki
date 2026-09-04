# Documentation Conventions

WikiAI docs follow Diátaxis for information type and these writing rules for voice.

## Information types

- **Tutorials** (`docs/tutorials/`): learning-oriented. Hold the reader's hand from zero to a working result.
- **How-to guides** (`docs/how-to/`): goal-oriented. One job per page. Skip the lecture.
- **Reference** (`docs/reference/`): information-oriented. Exhaustive and exact. Match the running code.
- **Explanation** (`docs/explanation/`): understanding-oriented. Why the product works this way. Label target design versus shipped MVP.

Do not mix these types on one page. Link across them instead.

## Voice and structure

- Write in clear operational English.
- Use active voice and present tense. Write "Click Save", not "The Save button should be clicked."
- Front-load meaning. Write "Deploy the app", not "In order to deploy the app..."
- Keep one idea per sentence.
- Prefer behavior-oriented headings over file-oriented headings.
- Assume the reader did not read the previous page. Link generously.
- Define jargon on first use, or link to the [glossary](../glossary.md). Avoid idioms and slang.

## Formatting

- Use backticks for identifiers, APIs, tables, metrics, file paths, button names, and UI elements.
- Specify a language on every fenced code block.
- Every code block must be copy-paste runnable, or clearly marked as pseudo-code.
- Use realistic domain names (`quantum-computing`, `contributor@example.com`). Do not use `foo`/`bar` unless showing abstract syntax.
- Prefer ASCII diagrams and Mermaid over screenshots. If you add an image, include alt text.
- Keep Markdown ASCII-friendly unless the file already requires otherwise.

## Callouts

Use sparingly:

```markdown
> **Note:** Extra context that is safe to skip.

> **Warning:** A likely failure if the reader ignores this.

> **Danger:** Data loss, security, or production-auth risk.
```

## Defaults and workflows

- State defaults and assumptions explicitly when you make a choice.
- When documenting workflows, use ordered lists.
- When documenting policies or rules, use flat bullet lists.
- Keep architecture guidance concrete enough to implement without further product decisions.

## Accuracy and maintenance

- Verify commands and API shapes against the current code. Do not write from memory.
- When code changes, change the docs in the same pull request.
- Separate target architecture from shipped MVP behavior. If a feature is not in the running code, say so.
- Do not invent rate limits, auth factors, or infrastructure that the MVP does not implement.
- Do not publish placeholder text ("TODO: fill this in later") in hub docs.
- Update [CHANGELOG.md](../../CHANGELOG.md) for user-visible API or workflow changes. Commit messages are not the changelog.
- Run `npm run check:docs` before submitting documentation. It runs Markdown linting, local and external link checks, and spell checking.
