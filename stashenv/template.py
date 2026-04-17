"""Template support: render a .env profile with variable substitution."""

import re
from typing import Optional

from stashenv.store import load_profile
from stashenv.export import env_to_dict, dict_to_env

_PLACEHOLDER_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render_template(template_text: str, context: dict) -> str:
    """Replace {{KEY}} placeholders in template_text with values from context."""
    def replacer(match):
        key = match.group(1)
        if key not in context:
            raise KeyError(f"Template placeholder '{{{{key}}}}' not found in context")
        return context[key]

    return _PLACEHOLDER_RE.sub(replacer, template_text)


def render_profile(
    project_dir: str,
    profile: str,
    password: str,
    context: Optional[dict] = None,
) -> str:
    """Load a profile and render any {{KEY}} placeholders using the profile's own
    values merged with an optional extra context dict.

    Returns the rendered .env text.
    """
    env_text = load_profile(project_dir, profile, password)
    env_dict = env_to_dict(env_text)

    merged_context = dict(env_dict)
    if context:
        merged_context.update(context)

    rendered_dict = {}
    for key, value in env_dict.items():
        rendered_dict[key] = render_template(value, merged_context)

    return dict_to_env(rendered_dict)


def list_placeholders(template_text: str) -> list:
    """Return a sorted list of unique placeholder names found in template_text."""
    return sorted(set(_PLACEHOLDER_RE.findall(template_text)))
