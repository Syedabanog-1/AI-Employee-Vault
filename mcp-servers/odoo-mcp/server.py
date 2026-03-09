#!/usr/bin/env python3
"""
Odoo MCP Server
Provides tools for interacting with Odoo via JSON-RPC and XML-RPC
through the Model Context Protocol.
"""

import asyncio
import logging
import os
import json
import xmlrpc.client
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, Any, List, Optional

from mcp.server import Server
from mcp.types import Tool

# Load env from .env file if available
try:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).parent.parent.parent / '.env')
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Credentials ---
ODOO_URL      = os.getenv('ODOO_URL', '').rstrip('/')
ODOO_DB       = os.getenv('ODOO_DB', '')
ODOO_USER     = os.getenv('ODOO_USER', '')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')
DRY_RUN       = os.getenv('DRY_RUN', 'false').lower() == 'true'


# ── Helpers ──────────────────────────────────────────────────────────────────

class _TimeoutTransport(xmlrpc.client.SafeTransport):
    """XML-RPC transport with configurable timeout."""
    def __init__(self, timeout=20, **kwargs):
        super().__init__(**kwargs)
        self._timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self._timeout
        return conn


def _xmlrpc_proxy(path: str):
    return xmlrpc.client.ServerProxy(
        f'{ODOO_URL}{path}',
        transport=_TimeoutTransport(timeout=20)
    )


def _xmlrpc_models():
    return _xmlrpc_proxy('/xmlrpc/2/object')


def _authenticate_xmlrpc() -> Optional[int]:
    """Returns uid on success, None on failure."""
    try:
        common = _xmlrpc_proxy('/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        return uid if uid else None
    except Exception as e:
        logger.error(f"XML-RPC auth error: {e}")
        return None


def _session_post(endpoint: str, params: dict) -> dict:
    """Open a cookie session, authenticate, then POST to the given endpoint."""
    import http.cookiejar
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    def _call(url, data):
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'}
        )
        return json.loads(opener.open(req, timeout=20).read())

    # 1. Authenticate
    auth = _call(f'{ODOO_URL}/web/session/authenticate', {
        'jsonrpc': '2.0', 'method': 'call', 'id': 1,
        'params': {'db': ODOO_DB, 'login': ODOO_USER, 'password': ODOO_PASSWORD}
    })
    uid = auth.get('result', {}).get('uid')
    if not uid:
        return {'error': 'Authentication failed'}

    # 2. Call the target endpoint
    result = _call(f'{ODOO_URL}{endpoint}', {
        'jsonrpc': '2.0', 'method': 'call', 'id': 2,
        'params': params
    })
    return result.get('result', result.get('error', {}))


# ── MCP Server ────────────────────────────────────────────────────────────────

class OdooMCP:
    def __init__(self):
        self.server = Server("odoo-mcp")
        self._setup_handlers()

    def _setup_handlers(self):

        tools = [
            Tool(
                name="odoo_get_user_info",
                description="Get the current authenticated Odoo user's info",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="odoo_post_message",
                description="Post a message or internal note on any Odoo record's chatter",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model":      {"type": "string", "description": "Odoo model name, e.g. res.partner, sale.order", "default": "res.partner"},
                        "record_id":  {"type": "integer", "description": "ID of the record to post on"},
                        "body":       {"type": "string", "description": "Message body text"},
                        "note":       {"type": "boolean", "description": "True = internal note, False = public message", "default": True}
                    },
                    "required": ["body"]
                }
            ),
            Tool(
                name="odoo_get_contacts",
                description="Search and list contacts (res.partner) in Odoo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search": {"type": "string", "description": "Name or email to search for (leave empty for all)"},
                        "limit":  {"type": "integer", "description": "Max results to return", "default": 10}
                    }
                }
            ),
            Tool(
                name="odoo_get_invoices",
                description="List invoices from Odoo accounting",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "description": "Invoice state: draft, posted, cancel, or all",
                            "default": "all"
                        },
                        "limit": {"type": "integer", "description": "Max results", "default": 10}
                    }
                }
            ),
            Tool(
                name="odoo_search_records",
                description="Search any Odoo model by domain filter",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model":  {"type": "string", "description": "Model name e.g. sale.order, project.task"},
                        "domain": {"type": "string", "description": "JSON domain filter e.g. [[\"state\",\"=\",\"sale\"]]", "default": "[]"},
                        "fields": {"type": "string", "description": "Comma-separated field names to return", "default": "id,name"},
                        "limit":  {"type": "integer", "description": "Max results", "default": 10}
                    },
                    "required": ["model"]
                }
            ),
        ]

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "odoo_get_user_info":
                return [await self.get_user_info()]
            elif name == "odoo_post_message":
                return [await self.post_message(arguments)]
            elif name == "odoo_get_contacts":
                return [await self.get_contacts(arguments)]
            elif name == "odoo_get_invoices":
                return [await self.get_invoices(arguments)]
            elif name == "odoo_search_records":
                return [await self.search_records(arguments)]
            else:
                raise ValueError(f"Unknown tool: {name}")

    # ── Tool implementations ──────────────────────────────────────────────────

    async def get_user_info(self) -> Dict[str, Any]:
        uid = _authenticate_xmlrpc()
        if not uid:
            return {"success": False, "error": "Authentication failed"}
        try:
            models = _xmlrpc_models()
            info = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.users', 'read', [[uid]],
                {'fields': ['name', 'email', 'partner_id', 'login']}
            )
            return {"success": True, "user": info[0] if info else {}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def post_message(self, args: dict) -> Dict[str, Any]:
        body       = args.get('body', '')
        model      = args.get('model', 'res.partner')
        note       = args.get('note', True)
        record_id  = args.get('record_id')

        if DRY_RUN:
            return {"success": True, "dry_run": True, "body": body, "model": model}

        # Default to the user's own partner if no record_id given
        if not record_id:
            uid = _authenticate_xmlrpc()
            if not uid:
                return {"success": False, "error": "Authentication failed"}
            models = _xmlrpc_models()
            user_info = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.users', 'read', [[uid]], {'fields': ['partner_id']}
            )
            record_id = user_info[0]['partner_id'][0]

        subtype = 'mail.mt_note' if note else 'mail.mt_comment'
        try:
            result = _session_post('/mail/message/post', {
                'thread_model': model,
                'thread_id': record_id,
                'post_data': {
                    'body': body,
                    'message_type': 'comment',
                    'subtype_xmlid': subtype
                }
            })
            msg_id = result.get('message_id') if isinstance(result, dict) else None
            return {
                "success": True,
                "message_id": msg_id,
                "model": model,
                "record_id": record_id,
                "body": body,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_contacts(self, args: dict) -> Dict[str, Any]:
        search = args.get('search', '')
        limit  = int(args.get('limit', 10))
        uid    = _authenticate_xmlrpc()
        if not uid:
            return {"success": False, "error": "Authentication failed"}
        try:
            domain = [['name', 'ilike', search]] if search else []
            models = _xmlrpc_models()
            records = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'search_read', [domain],
                {'fields': ['id', 'name', 'email', 'phone', 'is_company'], 'limit': limit}
            )
            return {"success": True, "count": len(records), "contacts": records}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_invoices(self, args: dict) -> Dict[str, Any]:
        state = args.get('state', 'all')
        limit = int(args.get('limit', 10))
        uid   = _authenticate_xmlrpc()
        if not uid:
            return {"success": False, "error": "Authentication failed"}
        try:
            domain = [['move_type', 'in', ['out_invoice', 'out_refund']]]
            if state != 'all':
                domain.append(['state', '=', state])
            models = _xmlrpc_models()
            records = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'account.move', 'search_read', [domain],
                {'fields': ['id', 'name', 'partner_id', 'amount_total', 'state', 'invoice_date'], 'limit': limit}
            )
            return {"success": True, "count": len(records), "invoices": records}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search_records(self, args: dict) -> Dict[str, Any]:
        model  = args.get('model', '')
        domain = json.loads(args.get('domain', '[]'))
        fields = [f.strip() for f in args.get('fields', 'id,name').split(',')]
        limit  = int(args.get('limit', 10))
        uid    = _authenticate_xmlrpc()
        if not uid:
            return {"success": False, "error": "Authentication failed"}
        try:
            models = _xmlrpc_models()
            records = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                model, 'search_read', [domain],
                {'fields': fields, 'limit': limit}
            )
            return {"success": True, "model": model, "count": len(records), "records": records}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run(self):
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def serve():
    server = OdooMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(serve())
