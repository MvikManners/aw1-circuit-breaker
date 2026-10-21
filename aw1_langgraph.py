import json, urllib.request, urllib.error, time, hmac, hashlib
from typing import Dict, Any

GATEWAY_URL = 'https://p20.laveto.net/wisdom/api/v1/intercept'
BURN_URL = 'https://p20.laveto.net/wisdom/api/v1/token/burn'
import os

GATEWAY_URL = os.getenv('AW1_GATEWAY_URL', 'https://p20.laveto.net/wisdom/api/v1/intercept')
BURN_URL = os.getenv('AW1_BURN_URL', 'https://p20.laveto.net/wisdom/api/v1/token/burn')
KEYS = {
    'treasury-agent-prod': os.getenv('AW1_KEY_TREASURY', ''),
    'agent-alpha-01': os.getenv('AW1_KEY_ALPHA', ''),
    'worker-agent': os.getenv('AW1_KEY_WORKER', ''),
    'test-agent': os.getenv('AW1_KEY_TEST', '')
}

def auth_headers(actor: str, tool: str, payload: str):
    sec = KEYS.get(actor, 'aw1_sec_dev_dummy_key_000000000000')
    ts = int(time.time())
    dig = hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]
    sig = hmac.new(sec.encode('utf-8'), f"{ts}:{actor}:{tool}:{dig}".encode('utf-8'), hashlib.sha256).hexdigest()[:32]
    return {
        'Content-Type': 'application/json',
        'X-AW1-Actor-Id': actor,
        'X-AW1-Timestamp': str(ts),
        'X-AW1-Signature': sig
    }

def intercept_tool_call(actor: str, tool: str, payload: str):
    data = json.dumps({'actor_id': actor, 'tool_name': tool, 'payload': payload}).encode('utf-8')
    req = urllib.request.Request(GATEWAY_URL, data=data, headers=auth_headers(actor, tool, payload))
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {'permitted': False, 'status': 'HALT_AND_CONTAIN', 'reason': f'HTTP {e.code}: {e.read().decode()}', 'token': None}
    except Exception as e:
        return {'permitted': False, 'status': 'HALT_AND_CONTAIN', 'reason': str(e), 'token': None}

def burn_execution_token(token: str, actor: str, tool: str, payload: str):
    data = json.dumps({'token': token, 'actor_id': actor, 'tool_name': tool, 'payload': payload}).encode('utf-8')
    req = urllib.request.Request(BURN_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'valid': False, 'reason': str(e)}

def create_guarded_tool_node(tools_by_name: Dict[str, Any], actor_id: str = 'treasury-agent-prod'):
    class ToolMsg:
        def __init__(self, content, tool_call_id, status='success', kwargs=None):
            self.content, self.tool_call_id, self.status, self.additional_kwargs = content, tool_call_id, status, kwargs or {}

    def node(state):
        msgs = state.get('messages', [])
        if not msgs:
            return {'messages': []}
        calls = getattr(msgs[-1], 'tool_calls', []) or (msgs[-1].get('tool_calls', []) if isinstance(msgs[-1], dict) else [])
        out = []
        for c in calls:
            name = c.get('name') if isinstance(c, dict) else c.name
            args = c.get('args') if isinstance(c, dict) else c.args
            cid = c.get('id') if isinstance(c, dict) else c.id
            payload = json.dumps(args, sort_keys=True) if isinstance(args, dict) else str(args)

            v = intercept_tool_call(actor_id, name, payload)
            if not v.get('permitted'):
                out.append(ToolMsg(f"🚨 [CIRCUIT BREAKER CONTAINMENT] {v.get('reason')}", cid, 'error'))
                continue

            b = burn_execution_token(v.get('token'), actor_id, name, payload)
            if not b.get('valid'):
                out.append(ToolMsg(f"🚨 [REPLAY PROTECTION] Token burn failed: {b.get('reason')}", cid, 'error'))
                continue

            fn = tools_by_name.get(name)
            if not fn:
                out.append(ToolMsg(f"Tool '{name}' not registered.", cid, 'error'))
                continue

            try:
                res = fn(**args) if isinstance(args, dict) else fn(args)
                out.append(ToolMsg(str(res), cid, 'success', {'aw1_token': v.get('token'), 'burn_nonce': b.get('nonce')}))
            except Exception as ex:
                out.append(ToolMsg(f'Execution error: {str(ex)}', cid, 'error'))
        return {'messages': out}

    return node