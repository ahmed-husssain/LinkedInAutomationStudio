"""
Unit Tests for Diagram Engine (D2, Excalidraw, and Diagram Package Generators).
Verifies decoupled schema generation, D2 URL compression, and artifact compilation.
"""

import zlib
import base64
import urllib.parse
from pathlib import Path

from src.engines.diagram_engine import (
    build_d2_script,
    build_d2_playground_url,
    build_excalidraw_json,
    generate_diagram_package,
    generate_diagram_package_async,
)


def test_build_d2_script_syntax_and_nodes():
    """Verifies that build_d2_script generates valid declarative D2 script with topology nodes."""
    script = build_d2_script("jwt_vs_sessions", "The JWT Revocation Dilemma", theme="cyan")
    assert "direction: right" in script
    assert "The JWT Revocation Dilemma" in script
    assert "ingress:" in script
    assert "Edge Gateway" in script
    assert "Redis Blocklist" in script
    assert "client -> ingress:" in script


def test_build_d2_playground_url_compression():
    """Verifies that the D2 URL can be decompressed back to the exact original script."""
    original_script = "direction: right\na -> b: Request"
    url = build_d2_playground_url(original_script)
    assert url.startswith("https://play.d2lang.com/?script=")

    # Extract encoded parameter and roundtrip verify
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    encoded_str = query_params["script"][0]

    raw_compressed = base64.b64decode(encoded_str)
    decompressed = zlib.decompress(raw_compressed, -zlib.MAX_WBITS).decode("utf-8")
    assert decompressed == original_script


def test_build_excalidraw_json_schema():
    """Verifies Excalidraw JSON conforms to standard schema with elements, arrows, and dark theme."""
    data = build_excalidraw_json("jwt_vs_sessions", "The JWT Revocation Dilemma", theme="emerald")
    assert data["type"] == "excalidraw"
    assert data["version"] == 2
    assert data["appState"]["theme"] == "dark"

    elements = data["elements"]
    assert len(elements) >= 10

    # Ensure rectangle nodes, text labels, and arrows exist
    element_types = {el["type"] for el in elements}
    assert "rectangle" in element_types
    assert "text" in element_types
    assert "arrow" in element_types


def test_generate_diagram_package_async(tmp_path: Path):
    """Verifies that generate_diagram_package_async compiles PNG, D2, and Excalidraw files."""
    import asyncio
    res = asyncio.run(generate_diagram_package_async(
        topic_id="jwt_vs_sessions",
        title="The JWT Revocation Dilemma",
        output_dir=tmp_path,
        theme="cyan",
        overwrite=True,
    ))

    assert "png_path" in res and res["png_path"].exists()
    assert "d2_file" in res and res["d2_file"].exists()
    assert "excalidraw_file" in res and res["excalidraw_file"].exists()
    assert "d2_url" in res and res["d2_url"].startswith("https://play.d2lang.com")
    assert "profile" in res and res["profile"]["title"] == "The JWT Revocation Dilemma"


def test_generate_diagram_package_sync(tmp_path: Path):
    """Verifies synchronous entrypoint runs without raising loop conflicts."""
    res = generate_diagram_package(
        topic_id="consistent_hashing",
        title="Consistent Hashing Ring Topology",
        output_dir=tmp_path,
        theme="purple",
        overwrite=True,
    )
    assert res["png_path"].exists()
    assert res["d2_file"].exists()
    assert res["excalidraw_file"].exists()


def test_diagram_markup_escapes_html_injection():
    """Security Regression: Verifies that HTML injection payloads in title/tagline are properly escaped."""
    from src.engines.diagram_engine import _build_html_markup

    payload = '<img src=x onerror="alert(1)">'
    markup = _build_html_markup("test_topic", payload, "tag<script>alert(2)</script>", "cyan")

    assert payload not in markup
    assert "<script>alert(2)</script>" not in markup
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in markup
    assert "tag&lt;script&gt;alert(2)&lt;/script&gt;" in markup


def test_diagram_output_path_confinement(tmp_path: Path):
    """Security Regression: Verifies that directory traversal payloads in topic_id cannot escape target_dir."""
    from src.engines.diagram_engine import generate_diagram_package

    traversal_topic = "../../escaped_diagram"
    res = generate_diagram_package(
        topic_id=traversal_topic,
        title="Traversal Attack Test",
        output_dir=tmp_path,
        theme="cyan",
        overwrite=True,
    )
    # The generated artifacts must reside strictly inside tmp_path
    assert res["png_path"].resolve().is_relative_to(tmp_path.resolve())
    assert res["d2_file"].resolve().is_relative_to(tmp_path.resolve())
    assert res["excalidraw_file"].resolve().is_relative_to(tmp_path.resolve())
    assert not (tmp_path.parent / "escaped_diagram_architecture.d2").exists()


