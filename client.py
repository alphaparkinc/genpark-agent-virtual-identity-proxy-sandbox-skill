"""Virtual Identity Proxy Sandbox for Personal Agents.
100% Python Standard Library.
"""

import time
import hashlib
import hmac

class VirtualIdentityProxySandbox:
    """Manages ephemeral proxy identities, burner email/phone aliases, and scoped transaction signatures."""
    def __init__(self, master_secret="genpark_personal_agent_secret_key"):
        self.master_secret = master_secret.encode("utf-8")
        self.aliases = {}

    def create_persona_alias(self, user_id, service_domain, scope_tags=None, budget_cents=5000):
        salt = f"{user_id}:{service_domain}:{time.time()}".encode("utf-8")
        token_hash = hashlib.sha256(salt).hexdigest()[:10]
        proxy_email = f"agent-{token_hash}@{service_domain}.proxy.genpark.ai"
        proxy_phone = f"+1-555-01{int(token_hash[:4], 16) % 90 + 10}"

        alias_record = {
            "alias_id": token_hash,
            "user_id": user_id,
            "service_domain": service_domain,
            "proxy_email": proxy_email,
            "proxy_phone": proxy_phone,
            "scope_tags": scope_tags or ["read", "transact"],
            "budget_cents": budget_cents,
            "spent_cents": 0,
            "active": True
        }
        self.aliases[token_hash] = alias_record
        return alias_record

    def sign_proxy_request(self, alias_id, action, amount_cents=0):
        if alias_id not in self.aliases:
            raise ValueError(f"Unknown alias ID: {alias_id}")
        alias = self.aliases[alias_id]
        if not alias["active"]:
            raise PermissionError("Alias is deactivated or revoked")
        if alias["spent_cents"] + amount_cents > alias["budget_cents"]:
            raise ValueError(f"Budget exceeded: budget={alias['budget_cents']}, requested={amount_cents}")

        alias["spent_cents"] += amount_cents
        msg = f"{alias_id}:{action}:{amount_cents}:{time.time()}".encode("utf-8")
        sig = hmac.new(self.master_secret, msg, hashlib.sha256).hexdigest()
        return {
            "signature": sig,
            "alias_id": alias_id,
            "authorized_action": action,
            "amount_cents": amount_cents,
            "remaining_budget_cents": alias["budget_cents"] - alias["spent_cents"]
        }

    def revoke_alias(self, alias_id):
        if alias_id in self.aliases:
            self.aliases[alias_id]["active"] = False
            return True
        return False
