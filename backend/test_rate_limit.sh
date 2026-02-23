#!/bin/bash
# Rate limit integration test for Readly API
# Usage: ./test_rate_limit.sh [base_url]
# Expects backend running with: RATE_LIMIT_MAX=2 RATE_LIMIT_WINDOW_MINUTES=5

BASE_URL="${1:-http://localhost:8000}"
DEVICE_ID="test-device-$(date +%s)"
TEST_URL="https://readly.space"
PASS=0
FAIL=0

echo "============================================"
echo "  Readly Rate Limit Integration Test"
echo "============================================"
echo "API:       $BASE_URL"
echo "Device:    $DEVICE_ID"
echo "Test URL:  $TEST_URL"
echo "============================================"
echo ""

# Helper: check a condition
check() {
    local label="$1"
    local condition="$2"
    if eval "$condition"; then
        echo "  ✅ $label"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $label"
        FAIL=$((FAIL + 1))
    fi
}

# ---- Step 1: Health check ----
echo "▶ Step 1: Health check"
HEALTH=$(curl -s "$BASE_URL/health")
check "Health endpoint returns ok" "echo '$HEALTH' | grep -q 'ok'"
echo ""

# ---- Step 2: Check initial rate limit ----
echo "▶ Step 2: Check initial rate limit (fresh device)"
JOBS=$(curl -s "$BASE_URL/jobs?device_id=$DEVICE_ID")
echo "  Response: $JOBS"
REMAINING=$(echo "$JOBS" | python3 -c "import sys,json; print(json.load(sys.stdin)['rate_limit']['remaining'])")
MAX=$(echo "$JOBS" | python3 -c "import sys,json; print(json.load(sys.stdin)['rate_limit']['max_per_window'])")
WINDOW=$(echo "$JOBS" | python3 -c "import sys,json; print(json.load(sys.stdin)['rate_limit']['window_minutes'])")
echo "  Remaining: $REMAINING / $MAX  (window: ${WINDOW}min)"
check "Remaining equals max_per_window" "[ '$REMAINING' = '$MAX' ]"
check "window_minutes is present" "[ -n '$WINDOW' ]"
echo ""

# ---- Step 3: Run conversions until rate limited ----
echo "▶ Step 3: Run conversions until rate limited"
CONVERSION_NUM=0

while true; do
    CONVERSION_NUM=$((CONVERSION_NUM + 1))
    echo "  --- Conversion #$CONVERSION_NUM ---"

    # Use SSE endpoint, capture all events
    EVENTS=$(curl -s -N --max-time 120 \
        "$BASE_URL/convert/stream?url=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TEST_URL'))")&device_id=$DEVICE_ID")

    # Check if rate limited
    if echo "$EVENTS" | grep -q '"rate_limited"'; then
        echo "  🚫 Rate limited on conversion #$CONVERSION_NUM"
        RESET_SEC=$(echo "$EVENTS" | python3 -c "import sys,json; data=json.loads(sys.stdin.read().replace('data: ','')); print(data.get('reset_seconds',0))" 2>/dev/null)
        echo "  Reset in: ${RESET_SEC}s"
        check "Rate limit triggered at expected count" "[ '$CONVERSION_NUM' -gt '$MAX' ]"
        check "reset_seconds is present and > 0" "[ '${RESET_SEC:-0}' -gt 0 ]"
        break
    fi

    # Check if conversion succeeded or errored
    if echo "$EVENTS" | grep -q '"complete"'; then
        echo "  ✅ Conversion succeeded"
    elif echo "$EVENTS" | grep -q '"error"'; then
        echo "  ⚠️  Conversion error (non-rate-limit)"
        echo "  (Continuing — errors still count toward rate limit)"
    fi

    # Safety: don't loop forever
    if [ "$CONVERSION_NUM" -ge 20 ]; then
        echo "  ⛔ Safety limit reached (20 conversions). Stopping."
        FAIL=$((FAIL + 1))
        break
    fi

    echo ""
done
echo ""

# ---- Step 4: Verify /jobs shows rate limit info ----
echo "▶ Step 4: Verify /jobs after rate limit hit"
JOBS=$(curl -s "$BASE_URL/jobs?device_id=$DEVICE_ID")
REMAINING=$(echo "$JOBS" | python3 -c "import sys,json; print(json.load(sys.stdin)['rate_limit']['remaining'])")
RESET=$(echo "$JOBS" | python3 -c "import sys,json; print(json.load(sys.stdin)['rate_limit']['reset_seconds'])")
echo "  Remaining: $REMAINING, Reset seconds: $RESET"
check "Remaining is 0" "[ '$REMAINING' = '0' ]"
check "Reset seconds > 0" "[ '${RESET:-0}' -gt 0 ]"
echo ""

# ---- Step 5: Submit feedback ----
echo "▶ Step 5: Submit feedback"
FB_RESP=$(curl -s -X POST "$BASE_URL/feedback" \
    -H "Content-Type: application/json" \
    -d "{\"device_id\": \"$DEVICE_ID\", \"response\": \"want_more\", \"use_case\": \"automated test\", \"conversions_today\": $CONVERSION_NUM}")
echo "  Response: $FB_RESP"
check "Feedback accepted" "echo '$FB_RESP' | grep -q 'ok'"
echo ""

# ---- Step 6: Wait for reset ----
echo "▶ Step 6: Wait for rate limit reset"
if [ "${RESET:-0}" -gt 0 ] && [ "${RESET:-0}" -le 300 ]; then
    WAIT=$((RESET + 5))
    echo "  Waiting ${WAIT}s for reset..."
    for i in $(seq "$WAIT" -10 1); do
        printf "\r  ⏳ %ds remaining...  " "$i"
        sleep $(( i > 10 ? 10 : i ))
    done
    printf "\r  ⏳ Checking now...       \n"

    JOBS=$(curl -s "$BASE_URL/jobs?device_id=$DEVICE_ID")
    REMAINING=$(echo "$JOBS" | python3 -c "import sys,json; print(json.load(sys.stdin)['rate_limit']['remaining'])")
    echo "  Remaining after reset: $REMAINING"
    check "Rate limit restored after reset" "[ '${REMAINING:-0}' -gt 0 ]"
else
    echo "  Skipping (reset time ${RESET:-0}s > 5min — set RATE_LIMIT_WINDOW_MINUTES=5 for quick test)"
fi
echo ""

# ---- Summary ----
echo "============================================"
echo "  Results: $PASS passed, $FAIL failed"
echo "============================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
