from client import VirtualIdentityProxySandbox

sandbox = VirtualIdentityProxySandbox()

# Create alias for food delivery
alias = sandbox.create_persona_alias("user_alpha", "doordash", budget_cents=4000)
print("Generated Persona Alias:", alias["proxy_email"], alias["proxy_phone"])

# Authorize an order
sig_info = sandbox.sign_proxy_request(alias["alias_id"], "order_meal", amount_cents=2150)
print("Authorized Action:", sig_info["authorized_action"])
print("Remaining Budget (cents):", sig_info["remaining_budget_cents"])
print("HMAC Signature:", sig_info["signature"][:16], "...")
