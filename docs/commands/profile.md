# /reforge.profile

Generate a language-specific and architecture-specific extraction profile.

## Syntax

```
/reforge.profile [--update]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--update` | No | Add or remove languages without replacing the entire profile |

## What It Does

This command gathers your project's technology stack (programming languages, frameworks, architectural patterns) and generates a tailored extraction profile at `.reforge/memory/extraction-profile.md`. The `/reforge.extract` command loads this profile automatically during initialization.

The profile command supports **auto-discovery** -- it can scan your codebase for file extensions to detect languages when you don't declare them explicitly. The LLM generates extraction rules for any declared language from its training knowledge; there is no finite "supported languages" list.

For each declared language, the profile generates rules covering:

1. **Type system quirks** -- language-specific type behaviors affecting extraction accuracy
2. **Operator differences** -- operators that could be misrecorded or paraphrased
3. **Naming conventions** -- case sensitivity rules and identifier patterns
4. **Common pitfalls** -- extraction errors specific to the language
5. **Framework patterns** -- framework-specific extraction guidance

If you declare architectural patterns (layered, microservices, event-driven, etc.), the profile also generates guidance on where business rules, data access, workflows, and integration points typically reside.

## Prerequisites

- `.reforge/memory/` directory must exist (run `/reforge.init` first, or create manually)

## Output

- `.reforge/memory/extraction-profile.md` -- language and architecture extraction rules

## Example

=== "Claude Code"

    ```
    /reforge.profile
    /reforge.profile --update
    ```

=== "GitHub Copilot"

    ```
    @reforge.profile
    @reforge.profile --update
    ```

## Related Commands

- [`/reforge.init`](init.md) -- initialize project context (run before profile for better defaults)
- [`/reforge.extract`](extract.md) -- extract knowledge using the profile's language-specific guidance
