"""Tests for release metadata and translation completeness."""

import json
from pathlib import Path
import re


ROOT = Path(__file__).parents[1]
INTEGRATION = ROOT / "custom_components" / "portfolio_tracker"


def _leaf_paths(value, prefix: tuple[str, ...] = ()) -> set[tuple[str, ...]]:
    if isinstance(value, dict):
        return {
            path
            for key, child in value.items()
            for path in _leaf_paths(child, (*prefix, key))
        }
    return {prefix}


def test_translation_files_have_the_same_shape() -> None:
    canonical = json.loads((INTEGRATION / "strings.json").read_text(encoding="utf-8"))
    expected = _leaf_paths(canonical)

    for language in ("de", "en", "fr", "it"):
        translated = json.loads(
            (INTEGRATION / "translations" / f"{language}.json").read_text(
                encoding="utf-8"
            )
        )
        assert _leaf_paths(translated) == expected


def test_release_versions_and_marketplace_category_are_consistent() -> None:
    manifest = json.loads((INTEGRATION / "manifest.json").read_text(encoding="utf-8"))
    const_source = (INTEGRATION / "const.py").read_text(encoding="utf-8")
    card_source = (INTEGRATION / "frontend" / "portfolio-asset-card.js").read_text(
        encoding="utf-8"
    )
    loader_source = (
        INTEGRATION / "frontend" / "portfolio-asset-card-loader.js"
    ).read_text(encoding="utf-8")
    version = manifest["version"]

    assert manifest["categories"] == ["finance"]
    assert re.search(rf'FRONTEND_VERSION: Final = "{re.escape(version)}"', const_source)
    assert f'const CARD_VERSION = "{version}";' in card_source
    assert f"portfolio-asset-card.js?v={version}" in loader_source
