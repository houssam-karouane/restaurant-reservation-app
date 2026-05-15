#!/usr/bin/env bash
# Re-import the Restaurant Reservation Zabbix templates after a Railway
# restart wipes volumes. Idempotent: --rules updateExisting:true.
#
# Usage:
#   ZABBIX_URL=https://zabbix.up.railway.app \
#   ZABBIX_USER=Admin \
#   ZABBIX_PASSWORD=... \
#   ./import_templates.sh
#
# Requires curl + jq.

set -euo pipefail

ZABBIX_URL="${ZABBIX_URL:?ZABBIX_URL is required, e.g. https://zabbix.up.railway.app}"
ZABBIX_USER="${ZABBIX_USER:-Admin}"
ZABBIX_PASSWORD="${ZABBIX_PASSWORD:?ZABBIX_PASSWORD is required}"

API="${ZABBIX_URL%/}/api_jsonrpc.php"
TEMPLATE_DIR="$(cd "$(dirname "$0")/../../zabbix" && pwd)"

echo "Logging in to $API ..."
AUTH=$(curl -fsS -X POST -H "Content-Type: application/json-rpc" "$API" -d @- <<EOF | jq -r .result
{"jsonrpc":"2.0","method":"user.login","params":{"username":"$ZABBIX_USER","password":"$ZABBIX_PASSWORD"},"id":1}
EOF
)

if [ -z "$AUTH" ] || [ "$AUTH" = "null" ]; then
  echo "Authentication failed" >&2
  exit 1
fi

import_one() {
  local file="$1"
  echo "Importing $(basename "$file") ..."
  local body
  body=$(cat "$file" | jq -Rs '{
    jsonrpc:"2.0",
    method:"configuration.import",
    params:{
      format:"yaml",
      source:.,
      rules:{
        templates:{createMissing:true, updateExisting:true},
        items:{createMissing:true, updateExisting:true},
        triggers:{createMissing:true, updateExisting:true},
        httptests:{createMissing:true, updateExisting:true},
        valueMaps:{createMissing:true, updateExisting:true}
      }
    },
    auth:"'"$AUTH"'",
    id:2
  }')
  curl -fsS -X POST -H "Content-Type: application/json-rpc" "$API" -d "$body" | jq .
}

for tpl in "$TEMPLATE_DIR"/*.yaml; do
  [ -f "$tpl" ] || continue
  import_one "$tpl"
done

echo "Done."
