import sys
import json
from client import VirtualIdentityProxySandbox

sandbox = VirtualIdentityProxySandbox()

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agent-virtual-identity-proxy-sandbox-skill", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "create_alias",
                        "description": "Create an ephemeral virtual proxy identity for interacting with external services",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "service_domain": {"type": "string"},
                                "budget_cents": {"type": "number"}
                            },
                            "required": ["user_id", "service_domain"]
                        }
                    },
                    {
                        "name": "sign_request",
                        "description": "Cryptographically sign an action under a delegated proxy alias with budget constraint",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "alias_id": {"type": "string"},
                                "action": {"type": "string"},
                                "amount_cents": {"type": "number"}
                            },
                            "required": ["alias_id", "action"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "create_alias":
            res = sandbox.create_persona_alias(args["user_id"], args["service_domain"], budget_cents=args.get("budget_cents", 5000))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tool_name == "sign_request":
            res = sandbox.sign_proxy_request(args["alias_id"], args["action"], args.get("amount_cents", 0))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_res = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
