"""
Topic Pool & Data Models for LinkedIn Automation Studio.
Contains the curated pool of 12 high-engagement system design & backend topics.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

from src.config.settings import VIDEOS_DIR, THUMBNAILS_DIR


@dataclass
class TopicAngle:
    label: str
    desc: str
    text: str


@dataclass
class Topic:
    id: str
    title: str
    tagline: str
    angles: List[TopicAngle]
    questions: List[str]
    subject: Optional[str] = None
    video_filename: Optional[str] = None
    thumb_filename: Optional[str] = None

    @property
    def video_path(self) -> Optional[Path]:
        if self.video_filename:
            path = VIDEOS_DIR / self.video_filename
            return path if path.exists() else None
        return None

    @property
    def thumb_path(self) -> Optional[Path]:
        if self.thumb_filename:
            path = THUMBNAILS_DIR / self.thumb_filename
            return path if path.exists() else None
        return None

    @property
    def has_video(self) -> bool:
        return self.video_path is not None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "tagline": self.tagline,
            "subject": self.subject or self.title,
            "has_video": self.has_video,
            "angles": [
                {"label": a.label, "desc": a.desc, "text": a.text}
                for a in self.angles
            ],
            "questions": list(self.questions),
        }


TOPIC_POOL: List[Topic] = [
    Topic(
        id="oauth",
        title="How OAuth 2.0 & PKCE Protect Apps",
        subject="OAuth 2.0 & PKCE Security",
        tagline="Why third-party apps never see your password (and why PKCE is mandatory).",
        video_filename="OAuthScene.mp4",
        thumb_filename="OAuthThumbnail.png",
        angles=[
            TopicAngle(
                label="The 4-Step Auth Code Flow",
                desc="Consent -> Auth Code -> Access Token -> User Profile",
                text="• Step 1: User logs into Google & approves app permissions.\n"
                     "• Step 2: Google redirects back with a temporary one-time Auth Code (code=xyz).\n"
                     "• Step 3: Backend exchanges the code for a scoped Access Token (JWT).\n"
                     "• Step 4: Backend fetches the profile with the Bearer token without ever seeing the password."
            ),
            TopicAngle(
                label="Why PKCE is Mandatory for Mobile & SPAs",
                desc="Protecting public clients without backend secrets",
                text="• Traditional OAuth requires a Client Secret stored on a backend server.\n"
                     "• Mobile apps and SPAs cannot keep client secrets safe from decompilation.\n"
                     "• PKCE (Proof Key for Code Exchange) uses dynamic code verifiers to stop authorization code interception."
            ),
        ],
        questions=[
            "In SPAs / Mobile, do you use PKCE directly or a BFF (Backend-for-Frontend)?",
            "How do you handle Token Refresh when an Access Token expires mid-session?",
            "Do you use self-contained JWTs or opaque tokens with Redis verification?",
            "What is the biggest security pitfall you've seen in OAuth implementations?",
        ],
    ),
    Topic(
        id="rate_limiter",
        title="Token Bucket: How Stripe Survives DDOS",
        subject="Token Bucket Rate Limiting",
        tagline="Permitting legitimate bursts while dropping abusive traffic in under 2ms.",
        video_filename="TokenBucketScene.mp4",
        thumb_filename="TokenBucketThumbnail_ManimCE_v0.22.0.png",
        angles=[
            TopicAngle(
                label="Burst Handling (The Core Superpower)",
                desc="Why 3 calls pass at 0ms, but 4th gets 429",
                text="• A bucket collects tokens at a steady rate (+1/s).\n"
                     "• If 3 calls hit at the exact same millisecond, all 3 pass because tokens are ready.\n"
                     "• When empty, the next call gets blocked with HTTP 429 until 1 second ticks."
            ),
            TopicAngle(
                label="Token Bucket vs Fixed Window",
                desc="Why fixed windows reset traffic spikes poorly",
                text="• Fixed Window just counts requests per minute, meaning users can send 100 calls at 0:59 and 100 at 1:01.\n"
                     "• Token Bucket solves this by maintaining a smooth refill rate regardless of clock windows."
            ),
        ],
        questions=[
            "Do you rate limit by IP address, user JWT, or API key?",
            "How do you expose rate limit headers back to mobile apps?",
            "What is the biggest production outage caused by a rate limiter?",
            "Do you rate limit at the API Gateway or in Redis middleware?",
        ],
    ),
    Topic(
        id="sql_index",
        title="Why UUIDv4 Primary Keys Ruin Postgres B-Trees",
        subject="Postgres B-Tree vs UUIDv4/UUIDv7",
        tagline="Random 128-bit page splits and cache thrashing vs sequential UUIDv7.",
        video_filename="SqlIndexScene.mp4",
        thumb_filename="SqlIndexThumbnail_ManimCE_v0.22.0.png",
        angles=[
            TopicAngle(
                label="The B-Tree Page Split Disaster",
                desc="Why random UUIDs trigger constant disk write amplification",
                text="• B-Trees keep leaf pages strictly sorted on disk.\n"
                     "• UUIDv4 keys are purely random, forcing Postgres to insert into random pages across the entire index.\n"
                     "• When pages fill up, 50% page splits double I/O and flush cache pages constantly."
            ),
            TopicAngle(
                label="The Solution: Time-Ordered UUIDv7 / ULID",
                desc="Preserving uniqueness while maintaining append-only sequential locality",
                text="• UUIDv7 embeds a millisecond UNIX timestamp in the most significant bits.\n"
                     "• Inserts always append to the right edge of the B-Tree leaf pages, eliminating random disk fragmentation."
            ),
        ],
        questions=[
            "Do you use BIGINT auto-increment, UUIDv4, or UUIDv7 in your primary tables?",
            "Have you experienced index bloat from random UUID inserts in production?",
            "What is your strategy for reindexing massive 500GB+ tables without downtime?",
            "Do you use partial indexes for tables with soft-deletes?",
        ],
    ),
    Topic(
        id="api_idempotency",
        title="API Idempotency: Never Charge Users Twice",
        subject="Payment API Idempotency",
        tagline="Deterministic idempotency keys and atomic DB locks under network retries.",
        video_filename="IdempotencyScene.mp4",
        thumb_filename="IdempotencyThumbnail_ManimCE_v0.22.0.png",
        angles=[
            TopicAngle(
                label="The Idempotency Key Workflow",
                desc="Client UUID -> Server Cache -> Safe Retry",
                text="• The mobile app generates a unique UUID (Idempotency-Key) before making the payment.\n"
                     "• The server caches the result in Redis with a 24-hour TTL.\n"
                     "• If the user taps 'Pay' twice or their Wi-Fi reconnects, the server returns the cached result without charging twice."
            ),
            TopicAngle(
                label="Network Timeout: Did payment succeed?",
                desc="Handling the dreaded 504 Gateway Timeout",
                text="• If a payment times out mid-flight, the client doesn't know if the money was deducted.\n"
                     "• Retrying with the same idempotency key makes retries 100% safe without duplicate charges."
            ),
        ],
        questions=[
            "What if a 2nd request arrives while the 1st is still processing?",
            "How long do you cache Idempotency Keys in Redis (24h vs 7 days)?",
            "Do you enforce idempotency keys on all POSTs or only payments?",
            "Do you generate the idempotency key on mobile or API gateway?",
        ],
    ),
    Topic(
        id="cache_aside",
        title="The Thundering Herd: Cache Stampedes in Redis",
        subject="Cache Stampede (Thundering Herd)",
        tagline="Why 10,000 simultaneous cache misses crash databases (and how XFetch saves them).",
        video_filename="CacheAsideScene.mp4",
        thumb_filename="CacheAsideThumbnail.png",
        angles=[
            TopicAngle(
                label="The Stampede Disaster",
                desc="When a hot key expires under 10k RPS",
                text="• When a viral post's cache key expires, 10,000 concurrent requests miss simultaneously.\n"
                     "• All 10,000 hit Postgres directly to recompute the same query, exhausting database connections instantly."
            ),
            TopicAngle(
                label="The Solution: Probabilistic Early Expiration (XFetch)",
                desc="Recomputing cache asynchronously before expiry",
                text="• A mathematical formula calculates the probability of early background refresh as TTL nears expiration.\n"
                     "• Only ONE background worker recomputes the data while users continue reading the cached copy seamlessly."
            ),
        ],
        questions=[
            "How does your team protect hot keys from Cache Stampedes (Mutex vs Early Refresh)?",
            "Do you use Stale-While-Revalidate caching headers in your API?",
            "What jitter strategy do you apply to TTLs to prevent synchronized expiration?",
            "Do you run Redis Cluster or Redis Sentinel in production?",
        ],
    ),
    Topic(
        id="message_queues",
        title="Why Message Queues Save Crashing APIs",
        subject="Message Queues (RabbitMQ & SQS)",
        tagline="Absorbing 10,000 req/s traffic spikes without crashing your database.",
        video_filename="QueueScene.mp4",
        thumb_filename="QueueThumbnail.png",
        angles=[
            TopicAngle(
                label="Peak Traffic Smoothing (Buffering)",
                desc="Absorbing 10,000 req/s while database writes at 500/s",
                text="• When traffic spikes 10x, synchronous APIs crash the database with connection timeouts.\n"
                     "• A message queue buffers the spike safely on disk, letting consumers process at a steady pace."
            ),
            TopicAngle(
                label="Decoupled Fault Tolerance",
                desc="Payment succeeds even if Email service is down",
                text="• If the email service crashes, messages stay queued.\n"
                     "• Once the email service recovers, it resumes processing without losing a single notification."
            ),
        ],
        questions=[
            "Do you use RabbitMQ, AWS SQS, or Apache Kafka in your stack?",
            "How do you handle Dead Letter Queues (DLQ) when a message fails 5 times?",
            "How do you prevent duplicate message processing when a consumer crashes mid-job?",
            "What metrics alert you that your queue lag is growing dangerously?",
        ],
    ),
    Topic(
        id="sharding_partitioning",
        title="The Read Replica Trap: Replication Lag",
        subject="Postgres Read Replicas & Replication Lag",
        tagline="Why adding read replicas broke user authentication after signup.",
        angles=[
            TopicAngle(
                label="The Signup Race Condition",
                desc="Write to primary, read from replica with 150ms lag -> 404",
                text="• Step 1: User signs up, backend commits INSERT to primary database.\n"
                     "• Step 2: Frontend immediately redirects to /dashboard, querying a read replica.\n"
                     "• Step 3: Replica is 150ms behind: user row does not exist yet, throwing a confusing 404.\n"
                     "• Step 4: User refreshes 1 second later and it works, leaving teams baffled."
            ),
            TopicAngle(
                label="Solution: Read-Your-Own-Writes Session Pinning",
                desc="Pinning sessions to primary after mutations",
                text="• Pin mutating user sessions to the primary database for 5 seconds after any write.\n"
                     "• Use monotonic read timestamps or Raft consensus to guarantee users never see data travel backward."
            ),
        ],
        questions=[
            "How does your team guarantee Read-Your-Own-Writes consistency behind replicas?",
            "What replication lag threshold triggers alerts in your production database?",
            "Do you use Citus, Vitess, or application-level routing for database scaling?",
            "What is the strangest bug caused by asynchronous database replication in your stack?",
        ],
    ),
    Topic(
        id="websockets_polling",
        title="10 Million Sockets: Scaling WebSockets",
        subject="WebSockets & C10M Concurrency",
        tagline="Epoll, memory footprint (10KB vs 1MB per socket), and reconnection storms.",
        angles=[
            TopicAngle(
                label="The Thundering Reconnect Storm",
                desc="When 500k clients reconnect simultaneously after restart",
                text="• When an API gateway restarts, 500,000 active clients disconnect and reconnect simultaneously.\n"
                     "• The sudden flood of SSL handshakes and token validations knocks over auth services instantly."
            ),
            TopicAngle(
                label="Solution: Jittered Backoff & Epoll Event Loops",
                desc="Spreading reconnect load and keeping idle sockets under 10KB RAM",
                text="• Clients must apply exponential backoff with randomized jitter to spread reconnections across minutes.\n"
                     "• Backends use Linux epoll / Go goroutines to hold 1M idle connections in memory."
            ),
        ],
        questions=[
            "How does your gateway survive 100,000 simultaneous WebSocket reconnections during a deployment?",
            "Do you use WebSockets or Server-Sent Events (SSE) for one-way streaming updates?",
            "What heartbeat / ping-pong interval do you use to detect dead mobile clients?",
            "How do you broadcast messages across 50 server nodes (Redis Pub/Sub vs Kafka)?",
        ],
    ),
    Topic(
        id="jwt_vs_sessions",
        title="The JWT Revocation Dilemma: Stateless Auth Myth",
        subject="JWT Invalidation & Distributed Sessions",
        tagline="Why revoking a compromised token forces you back to Redis state anyway.",
        angles=[
            TopicAngle(
                label="The 15-Minute Compromise Window",
                desc="Compromised tokens cannot be revoked before expiration",
                text="• A stolen JWT remains cryptographically valid across all microservices until its exp claim expires.\n"
                     "• If an employee is terminated or password is changed, you cannot revoke their JWT without a central blocklist."
            ),
            TopicAngle(
                label="Solution: Ephemeral Access + Rotating Refresh Tokens",
                desc="5-minute access tokens with instant refresh token family revocation",
                text="• Issue ultra-short 5-minute Access Tokens with RS256 asymmetric signatures.\n"
                     "• Pair with stateful, rotating Refresh Tokens in Redis that immediately invalidate token families upon reuse."
            ),
        ],
        questions=[
            "What TTL does your team configure on JWT access tokens in production (5m vs 1h)?",
            "How do you immediately revoke access when a user is terminated or changes password?",
            "Do you store refresh tokens in HttpOnly SameSite cookies or mobile SecureStore?",
            "Have you ever experienced CPU spikes from RS256 cryptographic verification at scale?",
        ],
    ),
    Topic(
        id="connection_pooling",
        title="TCP Port Exhaustion: Microservices Outage",
        subject="Ephemeral Port Exhaustion & PgBouncer",
        tagline="Why opening new HTTP connections exhausts 65,535 ports in TIME_WAIT.",
        angles=[
            TopicAngle(
                label="The EADDRNOTAVAIL Disaster",
                desc="2,000 RPS exhausts 65k outbound ports while CPU is only at 15%",
                text="• Opening a new HTTP request for every microservice call burns an ephemeral outbound TCP port.\n"
                     "• When closed, sockets stay in TIME_WAIT for 60 seconds: at 2,000 RPS, all 65,535 ports exhaust instantly."
            ),
            TopicAngle(
                label="Solution: Persistent Keep-Alive & PgBouncer",
                desc="Reusing pooled TCP connections and multiplexing DB threads",
                text="• Reusing pooled TCP connections via HTTP/2 and keep-alive eliminates TIME_WAIT port exhaustion.\n"
                     "• For databases, PgBouncer multiplexes 10,000 application threads over 50 dedicated Postgres connections."
            ),
        ],
        questions=[
            "What max idle connections per host do you configure in your HTTP clients?",
            "Do you run PgBouncer in transaction mode or session mode with Postgres?",
            "How do you diagnose EADDRNOTAVAIL socket exhaustion in containerized clusters?",
            "What connection checkout timeout (e.g. 2s vs 10s) do you enforce before throwing 503s?",
        ],
    ),
    Topic(
        id="optimistic_locking",
        title="Postgres MVCC & The Vacuum Bloat Nightmare",
        subject="Postgres MVCC & Autovacuum Bloat",
        tagline="How high-frequency UPDATEs create dead row tuples, turning a 10GB table into 200GB.",
        angles=[
            TopicAngle(
                label="The Dead Tuple Avalanche",
                desc="Postgres UPDATE writes a brand-new row version on disk",
                text="• In Postgres, UPDATE doesn't mutate rows in-place: it writes a new version and marks the old row dead.\n"
                     "• High-write tables accumulate millions of dead tuples, doubling disk size and slowing sequential scans to a crawl."
            ),
            TopicAngle(
                label="Solution: HOT Optimization & Autovacuum Tuning",
                desc="Heap-Only Tuples and table fillfactor tuning",
                text="• Heap-Only Tuple (HOT) updates avoid index pointer rewrites if modified columns aren't indexed.\n"
                     "• Lowering table fillfactor to 85 leaves room in data pages for updates without page splits."
            ),
        ],
        questions=[
            "How do you monitor dead tuple ratios and autovacuum lag across your Postgres clusters?",
            "Have you ever run pg_repack on a multi-terabyte production table without locking writes?",
            "Do you use Optimistic Version columns or SELECT FOR UPDATE for financial ledger mutations?",
            "What autovacuum vacuum_cost_limit do you configure on high-throughput NVMe drives?",
        ],
    ),
    Topic(
        id="bloom_filters",
        title="The 1-Billion URL Check: Bloom Filters in Bigtable",
        subject="Bloom Filters & In-Memory Bit Arrays",
        tagline="Preventing 99% of expensive disk seeks with a 1.2MB in-memory bit array.",
        angles=[
            TopicAngle(
                label="Zero False Negatives: The 0-Seek Shortcut",
                desc="If bit-check says NO, key 100% does not exist on disk",
                text="• If a user queries a non-existent record, querying disk SSTables wastes disk IOPs and latency.\n"
                     "• A Bloom Filter hashes keys across a tiny RAM bit array: if it says NO, the record 100% does not exist, skipping disk entirely."
            ),
            TopicAngle(
                label="Tuning False Positives & Memory Budget",
                desc="Achieving 1% false positive rate with only 9.6 bits per element",
                text="• Using optimal hash count k = (m/n) * ln(2), a 1% false positive rate requires only 9.6 bits per element.\n"
                     "• 1,000,000 URLs can be verified in 1.2MB of RAM, eliminating 99% of SSD disk reads."
            ),
        ],
        questions=[
            "Have you used Bloom Filters in Redis (RedisBloom) to prevent cache penetration attacks?",
            "What false positive rate (1% vs 0.1%) do you target when sizing your bit arrays?",
            "How do you handle key deletions in Bloom Filters when data is updated?",
            "At what cache miss volume does adding a Bloom filter become worth the RAM overhead?",
        ],
    ),
]


def get_topic_by_id(topic_id: str) -> Optional[Topic]:
    """Finds a topic by its unique slug identifier."""
    if not topic_id:
        return None
    cleaned = topic_id.strip().lower()
    return next((t for t in TOPIC_POOL if t.id.lower() == cleaned), None)
