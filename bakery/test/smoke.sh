#!/bin/bash
B=http://127.0.0.1:3000
P=0; F=0
T() { if [ "$2" = "1" ]; then echo "  PASS  $1"; P=$((P+1)); else echo "  FAIL  $1  ($3)"; F=$((F+1)); fi; }
CJ="Content-Type: application/json"
PY() { python3 -c "$1"; }

curl -s -c /tmp/ck_owner -X POST $B/api/login -H "$CJ" -d '{"phone":"079000000","password":"changeme"}' -o /dev/null
grep -q bk_sid /tmp/ck_owner && T "owner signs in" 1 || T "owner signs in" 0 "no cookie jar entry"
A="-b /tmp/ck_owner"

BN=$( curl -s $A $B/api/status | PY "import json,sys;print(json.load(sys.stdin).get('businessName'))")
[ "$BN" = "Mama G's Bakery House" ] && T "bootstrap carries the bakery name" 1 || T "bootstrap name" 0 "$BN"

REF="smoke-$(date +%s%N)"
R1=$(curl -s $A -X POST $B/api/sales -H "$CJ" -d "{\"client_ref\":\"$REF\",\"items\":[{\"product_id\":3,\"qty\":1}],\"method\":\"cash\"}" | PY "import json,sys;print(json.load(sys.stdin).get('replay'))")
R2=$(curl -s $A -X POST $B/api/sales -H "$CJ" -d "{\"client_ref\":\"$REF\",\"items\":[{\"product_id\":3,\"qty\":1}],\"method\":\"cash\"}" | PY "import json,sys;print(json.load(sys.stdin).get('replay'))")
[ "$R1" = "False" ] && [ "$R2" = "True" ] && T "replayed sale returns the original, not a duplicate" 1 || T "sale replay" 0 "$R1/$R2"

read ID AMT ST <<< $(curl -s $A "$B/api/expenses?from=2000-01-01&to=2999-12-31" | PY "import json,sys;e=json.load(sys.stdin)['expenses'][0];print(e['id'],e['amount'],e['updated_at'])")
curl -s -o /dev/null $A -X PUT $B/api/expenses/$ID -H "$CJ" -d "{\"amount\":$((AMT+100)),\"base_updated_at\":\"$ST\",\"client_ref\":\"smoke-e1-$$\"}"
CODE=$(curl -s -o /tmp/c409.json -w '%{http_code}' $A -X PUT $B/api/expenses/$ID -H "$CJ" -d "{\"amount\":1,\"base_updated_at\":\"$ST\",\"client_ref\":\"smoke-e2-$$\"}")
[ "$CODE" = "409" ] && T "stale offline edit refused with 409" 1 || T "stale edit 409" 0 "HTTP $CODE"
grep -q '"conflict"' /tmp/c409.json && grep -q 'server_updated_at' /tmp/c409.json && T "409 body carries both timestamps" 1 || T "409 body" 0 "$(head -c 100 /tmp/c409.json)"
CODE2=$(curl -s -o /dev/null -w '%{http_code}' $A -X PUT $B/api/expenses/$ID -H "$CJ" -d "{\"amount\":1,\"base_updated_at\":\"$ST\",\"client_ref\":\"smoke-e2-$$\"}")
[ "$CODE2" = "409" ] && T "the same ref keeps answering 409 (parked, never applied)" 1 || T "conflict repeatable" 0 "HTTP $CODE2"
AMT2=$(curl -s $A "$B/api/expenses?from=2000-01-01&to=2999-12-31" | PY "import json,sys;print([e for e in json.load(sys.stdin)['expenses'] if e['id']==int('$ID')][0]['amount'])")
[ "$AMT2" = "$((AMT+100))" ] && T "server value untouched by the stale edit" 1 || T "server untouched" 0 "$AMT2"

CID=$(curl -s $A -X POST $B/api/customers -H "$CJ" -d '{"name":"Smoke Cust","phone":"079555999"}' | PY "import json,sys;print(json.load(sys.stdin).get('id'))")
D1=$(curl -s $A -X DELETE $B/api/customers/$CID -H "$CJ" -d "{\"client_ref\":\"smoke-d1-$$\"}" | PY "import json,sys;print(json.load(sys.stdin).get('deleted'))")
D2=$(curl -s $A -X DELETE $B/api/customers/$CID -H "$CJ" -d "{\"client_ref\":\"smoke-d1-$$\"}" | PY "import json,sys;d=json.load(sys.stdin);print('ok' if (d.get('replay') or d.get('alreadyGone')) else 'BAD')")
[ "$D1" = "True" ] && [ "$D2" = "ok" ] && T "delete then replay is safe (no 404, no double delete)" 1 || T "delete replay" 0 "$D1/$D2"

curl -s -c /tmp/ck_staff -X POST $B/api/login -H "$CJ" -d '{"phone":"079111111","password":"staff123"}' -o /dev/null
PCODE=$(curl -s -o /dev/null -w '%{http_code}' -b /tmp/ck_staff -X PUT $B/api/products/3 -H "$CJ" -d '{"price":10}')
[ "$PCODE" = "403" ] && T "staff blocked from product edits" 1 || T "staff blocked" 0 "HTTP $PCODE"
RCODE=$(curl -s -o /dev/null -w '%{http_code}' -b /tmp/ck_staff "$B/api/reports/summary?from=2026-09-01&to=2026-09-27")
[ "$RCODE" = "403" ] && T "staff blocked from owner reports" 1 || T "staff reports" 0 "HTTP $RCODE"

M=$(curl -s $B/manifest.webmanifest | PY "import json,sys;d=json.load(sys.stdin);print(d['name'],'|',d['short_name'],'|',len(d['icons']))")
[ "$M" = "Mama G's Bakery House | Mama G's | 3" ] && T "manifest: name, short name, 3 icons" 1 || T "manifest" 0 "$M"
OKI=1; for f in icon-192.png icon-512.png icon-maskable-512.png apple-touch-icon.png favicon-32.png; do
  C=$(curl -s -o /dev/null -w '%{http_code}' $B/icons/$f); [ "$C" = "200" ] || OKI=0
done
[ "$OKI" = "1" ] && T "all five icon sizes served" 1 || T "icons" 0
SW=$(curl -s $B/sw.js | grep -c "icons/icon-512.png"); [ "$SW" = "1" ] && T "service worker precaches the logo" 1 || T "sw precache" 0 "$SW"
LOGO=$(curl -s $B/ | grep -c 'icons/favicon-32.png'); [ "$LOGO" = "1" ] && T "page head links the new favicon" 1 || T "favicon link" 0 "$LOGO"

echo
echo "  SMOKE: $P passed, $F failed"
exit $F
