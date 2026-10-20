"""
Unit Tests for SVG Micro-Diagram Primitives.
Verifies pure-SVG structure, Apple-grade specular styling, tabular metrics,
and direct in-line data labels without detached legends.
"""

from src.design_system.primitives import (
    render_database_cylinder,
    render_partitioned_queue,
    render_gateway_shield,
    render_directional_flow,
)


def test_render_database_cylinder():
    """Verifies 3D cylinder database primitive with replicas and tabular metrics."""
    svg = render_database_cylinder(
        x=50,
        y=50,
        width=140,
        height=160,
        label="PostgreSQL Primary",
        metric="p99 8.4ms",
        replicas=3,
        status="healthy",
    )
    assert '<g class="primitive-database"' in svg
    assert "PostgreSQL Primary" in svg
    assert "p99 8.4ms" in svg
    assert 'tabular-nums' in svg
    assert 'stroke-dasharray="3 3"' in svg  # Replica rings
    assert "#10b981" in svg  # Healthy beacon


def test_render_partitioned_queue():
    """Verifies streaming queue primitive with partition slots and lag indicator."""
    svg = render_partitioned_queue(
        x=200,
        y=100,
        width=240,
        height=90,
        partitions=4,
        topic="orders.checkout.v1",
        lag=142,
    )
    assert '<g class="primitive-queue"' in svg
    assert "orders.checkout.v1" in svg
    assert "LAG 142" in svg
    assert "P0" in svg
    assert "P1" in svg
    assert "P2" in svg
    assert "P3" in svg


def test_render_gateway_shield():
    """Verifies API Gateway shield primitive with specular bevel and rate limit badge."""
    svg = render_gateway_shield(
        x=10,
        y=20,
        width=120,
        height=130,
        label="Kong Gateway",
        rate_limit="25k req/s",
    )
    assert '<g class="primitive-gateway"' in svg
    assert "Kong Gateway" in svg
    assert "25k req/s" in svg
    assert "<polygon" not in svg  # Uses crisp path geometry
    assert "<circle" in svg       # Gateway core pulse


def test_render_directional_flow():
    """Verifies vector connection with direct in-line labeling (zero detached legends)."""
    svg = render_directional_flow(
        x1=100,
        y1=100,
        x2=400,
        y2=100,
        label="gRPC / Protobuf",
        accent="#38bdf8",
        animated=True,
    )
    assert '<g class="primitive-flow"' in svg
    assert "marker-end=" in svg
    assert "gRPC / Protobuf" in svg
    assert 'stroke-dasharray="6 4"' in svg  # Animated velocity flow


def test_render_full_width_topology():
    """Verifies edge-to-edge 880px distributed architecture topology."""
    from src.design_system.primitives import render_full_width_topology
    svg = render_full_width_topology(
        width=880,
        height=240,
        ingress_label="HAProxy L4",
        ingress_metric="1M rps",
        worker_label="Epoll Edge",
        worker_metric="10M Conns",
        queue_label="Kafka Bus",
        queue_metric="64 Partitions",
        store_label="Distributed Raft",
        store_metric="p99 2.1ms",
        accent="#38bdf8"
    )
    assert '<svg width="880" height="240"' in svg
    assert "HAProxy L4" in svg
    assert "Epoll Edge" in svg
    assert "Kafka Bus" in svg
    assert "Distributed Raft" in svg
    assert "p99 2.1ms" in svg
    assert 'filter="url(#topo-glow)"' in svg


def test_render_sequence_flow_svg():
    """Verifies horizontal temporal sequence flow SVG."""
    from src.design_system.primitives import render_sequence_flow_svg
    steps = ["TCP SYN", "HTTP 101 Upgrade", "Epoll Register", "Pub/Sub Broadcast", "ACK Frame"]
    svg = render_sequence_flow_svg(steps=steps, width=880, height=80, accent="#38bdf8")
    assert '<svg width="880" height="80"' in svg
    assert "01" in svg
    assert "05" in svg
    assert "TCP SYN" in svg
    assert "ACK Frame" in svg

