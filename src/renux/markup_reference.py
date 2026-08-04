"""Renders human-readable docs for renux's markup syntax from `renux.markup`.

This is the single place that turns the `renux.markup` registry into prose.
`--help` (renux.parser) and the TUI help screen (renux.screens.help) both
call this module, so a placeholder or filter added to `renux.markup` shows
up everywhere without further changes.
"""

from renux.markup import FILTERS, PLACEHOLDERS


def render_text() -> str:
    """Render the markup reference as plain text, for `--help`."""
    lines = ["markup syntax (usable in `replacement`):", ""]

    lines.append("  text transformations   {string|filter}")
    filters = ", ".join(FILTERS)
    lines.append(f"                          filters: {filters}")
    lines.append("")

    for placeholder in PLACEHOLDERS.values():
        lines.append(f"  {placeholder.syntax}")
        lines.append(f"      {placeholder.description}")

    lines.append("")
    lines.append("examples:")
    for placeholder in PLACEHOLDERS.values():
        if placeholder.example:
            lines.append(f'  renux my_files/ file "file_{placeholder.example}"')
    lines.append('  renux my_files "(.*)" "{filename|slugify}" -r')

    return "\n".join(lines)


def render_readme() -> str:
    """Render the markup reference as the README's `**Markup**` bullet list."""
    lines = ["- **Text transformations**: `{string|filter}`"]
    for name, filt in FILTERS.items():
        lines.append(f"  - `{name}`: {filt.description}")
    lines.append("")

    for placeholder in PLACEHOLDERS.values():
        label = placeholder.name.replace("_", " ").title()
        line = f"- **{label}**: `{placeholder.syntax}`"
        if placeholder.example:
            line += f", e.g., `{placeholder.example}`"
        lines.append(line)
        lines.append(f"  {placeholder.description}")

    return "\n".join(lines)


def render_markdown() -> str:
    """Render the markup reference as Markdown, for the TUI help screen."""
    lines = [
        "# Markup Syntax",
        "",
        "Use these placeholders in the **Replace with** field.",
        "",
    ]

    lines.append("## Text transformations")
    lines.append("`{string|filter}`")
    lines.append("")
    for name, filt in FILTERS.items():
        lines.append(f"- `{name}`: {filt.description}")
    lines.append("")

    for placeholder in PLACEHOLDERS.values():
        lines.append(f"## {placeholder.name}")
        lines.append(f"`{placeholder.syntax}`")
        lines.append("")
        lines.append(placeholder.description)
        if placeholder.example:
            lines.append("")
            lines.append(f"e.g. `{placeholder.example}`")
        lines.append("")

    lines.append("## Examples")
    for placeholder in PLACEHOLDERS.values():
        if placeholder.example:
            lines.append(f"- `file_{placeholder.example}`")
    lines.append("- `{filename|slugify}`")

    return "\n".join(lines)
