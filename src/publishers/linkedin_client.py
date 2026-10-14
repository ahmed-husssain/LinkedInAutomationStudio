"""
LinkedIn API REST Client & Safe Publisher.
Communicates with official LinkedIn REST API (/rest/posts) with built-in safety checks,
error handling, and safe simulation mode for test environments.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Optional
from pathlib import Path

from src.config.settings import LINKEDIN_ACCESS_TOKEN, LINKEDIN_AUTHOR_URN
from src.publishers.safety_guard import LinkedInSafetyGuard


class LinkedInClient:
    def __init__(
        self,
        access_token: Optional[str] = None,
        author_urn: Optional[str] = None,
        safety_guard: Optional[LinkedInSafetyGuard] = None
    ):
        self.access_token = (access_token or LINKEDIN_ACCESS_TOKEN or "").strip()
        self.author_urn = (author_urn or LINKEDIN_AUTHOR_URN or "").strip()
        self.safety_guard = safety_guard or LinkedInSafetyGuard()

    @property
    def is_configured(self) -> bool:
        """Returns True if live credentials are configured."""
        return bool(self.access_token and self.author_urn)

    def publish_post(self, text: str, media_path: Optional[Path] = None) -> Dict:
        """
        Publishes a post to LinkedIn. Guarded by safety cooldown.

        Args:
            text: Commentary text for the post.
            media_path: Optional path to an image or video asset.

        Returns:
            Dict containing success status, url/error, and post_id.
        """
        # 1. Enforce Cooldown Safety Guardrail
        if not self.safety_guard.can_publish_today():
            remaining = self.safety_guard.get_remaining_cooldown_hours()
            return {
                "success": False,
                "error": f"Safety Guardrail: Cooldown active. {remaining}h remaining before next post allowed.",
                "cooldown_active": True,
            }

        # 2. Simulation / Dry-run Mode
        if not self.is_configured:
            simulated_id = "simulated_urn_12345"
            self.safety_guard.record_successful_post(simulated_id)
            return {
                "success": True,
                "url": "https://www.linkedin.com/feed/ (Simulation: Set LINKEDIN_ACCESS_TOKEN in .env for live posting)",
                "post_id": simulated_id,
                "simulation": True,
                "note": "Guardrail passed. Post verified in simulation mode."
            }

        # 3. Live API Publishing
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202401",
            "Content-Type": "application/json"
        }

        payload = {
            "author": self.author_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED"
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://api.linkedin.com/rest/posts",
            data=req_data,
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:  # nosec: B310
                post_id = resp.headers.get("x-restli-id", "success")
                self.safety_guard.record_successful_post(post_id)
                return {
                    "success": True,
                    "url": f"https://www.linkedin.com/feed/update/{post_id}",
                    "post_id": post_id,
                    "simulation": False
                }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            return {
                "success": False,
                "error": f"LinkedIn API Error {e.code}: {err_body}",
                "status_code": e.code
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"Network Error reaching LinkedIn: {e.reason}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected Error: {str(e)}"
            }
