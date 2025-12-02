#!/bin/bash

# Script to monitor trip completion and test result endpoints
API_URL="https://ai-trip-planner-production-45dc.up.railway.app"
TRIP_ID="${1:-trip_9ba3f483a371}"  # Use provided trip ID or default

echo "=== Monitoring Trip: $TRIP_ID ==="
echo ""

MAX_CHECKS=60  # Check up to 60 times (5 minutes max)
CHECK_INTERVAL=5  # Check every 5 seconds

for i in $(seq 1 $MAX_CHECKS); do
  echo "[Check #$i] Fetching progress..."
  
  PROGRESS=$(curl -s "${API_URL}/api/trips/${TRIP_ID}/progress")
  STATUS=$(echo "$PROGRESS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
  PROGRESS_PCT=$(echo "$PROGRESS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('progress', 0))" 2>/dev/null)
  MESSAGE=$(echo "$PROGRESS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'N/A'))" 2>/dev/null)
  
  echo "  Status: $STATUS"
  echo "  Progress: $PROGRESS_PCT%"
  echo "  Message: $MESSAGE"
  echo ""
  
  if [ "$STATUS" = "completed" ]; then
    echo "✅ Trip planning completed!"
    echo ""
    break
  fi
  
  if [ "$STATUS" = "error" ]; then
    echo "❌ Trip planning failed!"
    echo "$PROGRESS" | python3 -m json.tool
    exit 1
  fi
  
  if [ $i -lt $MAX_CHECKS ]; then
    echo "Waiting ${CHECK_INTERVAL} seconds..."
    sleep $CHECK_INTERVAL
    echo ""
  fi
done

if [ "$STATUS" != "completed" ]; then
  echo "⚠️  Trip did not complete within expected time. Current status: $STATUS"
  echo "You can manually check later with:"
  echo "  curl -s ${API_URL}/api/trips/${TRIP_ID}/progress | python3 -m json.tool"
  exit 1
fi

echo "=== Testing Result Endpoints ==="
echo ""

# Test 1: Get HTML Result
echo "1. Testing HTML Result Endpoint (GET /api/trips/{trip_id}/result)..."
echo ""
RESULT_RESPONSE=$(curl -s "${API_URL}/api/trips/${TRIP_ID}/result")
RESULT_STATUS=$(echo "$RESULT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin) if sys.stdin.readable() else {}; print('success' if 'trip_id' in data else 'error')" 2>/dev/null)

if echo "$RESULT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('trip_id' in data)" 2>/dev/null | grep -q "True"; then
  echo "✅ HTML Result retrieved successfully!"
  echo ""
  echo "$RESULT_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Trip ID: {data['trip_id']}\")
html_len = len(data.get('html_content', ''))
print(f\"HTML Content Length: {html_len:,} characters\")
if html_len > 0:
    print(f\"HTML Preview (first 500 chars):\")
    print(data['html_content'][:500] + '...')
"
else
  echo "❌ Failed to retrieve result:"
  echo "$RESULT_RESPONSE"
fi

echo ""
echo ""

# Test 2: Get PDF Result
echo "2. Testing PDF Result Endpoint (GET /api/trips/{trip_id}/result/pdf)..."
echo ""
PDF_FILE="trip_result_${TRIP_ID}.pdf"

# Download PDF directly to file (binary mode)
HTTP_STATUS=$(curl -s -o "${PDF_FILE}" -w "%{http_code}" "${API_URL}/api/trips/${TRIP_ID}/result/pdf")

if [ "$HTTP_STATUS" = "200" ]; then
  if [ -f "${PDF_FILE}" ]; then
    PDF_SIZE=$(wc -c < "${PDF_FILE}" | tr -d ' ')
    PDF_SIZE_KB=$(echo "scale=2; $PDF_SIZE/1024" | bc 2>/dev/null || echo "N/A")
    PDF_HEADER=$(head -c 4 "${PDF_FILE}")
    
    echo "✅ PDF generated successfully!"
    echo "  HTTP Status: $HTTP_STATUS"
    echo "  PDF Size: $PDF_SIZE bytes ($PDF_SIZE_KB KB)"
    
    if [ "$PDF_HEADER" = "%PDF" ]; then
      echo "  ✅ PDF has valid header"
      echo "✅ PDF saved to: ${PDF_FILE}"
    else
      echo "  ⚠️  PDF header may be invalid (got: '$PDF_HEADER')"
    fi
  else
    echo "❌ PDF file was not created"
  fi
else
  echo "⚠️  PDF endpoint response:"
  echo "  HTTP Status: $HTTP_STATUS"
  if [ "$HTTP_STATUS" = "503" ] || [ "$HTTP_STATUS" = "500" ]; then
    echo "  Note: PDF generation may require WeasyPrint. Check if it's available."
  fi
  if [ -f "${PDF_FILE}" ]; then
    head -20 "${PDF_FILE}"
  fi
fi

echo ""
echo ""

# Test 3: Verify HTML content structure
echo "3. Analyzing HTML Content Structure..."
echo ""
if echo "$RESULT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('trip_id' in data)" 2>/dev/null | grep -q "True"; then
  echo "$RESULT_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
html = data.get('html_content', '')
if html:
    print(f\"✅ HTML content found\")
    print(f\"   Contains <html>: {'<html>' in html.lower()}\")
    print(f\"   Contains <body>: {'<body>' in html.lower()}\")
    print(f\"   Contains <head>: {'<head>' in html.lower()}\")
    # Count some common elements
    print(f\"   Number of <div> tags: {html.lower().count('<div')}\")
    print(f\"   Number of <p> tags: {html.lower().count('<p>')}\")
    print(f\"   Number of <h1> tags: {html.lower().count('<h1')}\")
else:
    print(\"❌ No HTML content found\")
"
fi

echo ""
echo "=== Testing Complete ==="
echo ""
echo "Summary:"
echo "  Trip ID: $TRIP_ID"
echo "  Status: $STATUS"
echo "  HTML Result: $([ \"$STATUS\" = \"completed\" ] && echo \"✅ Available\" || echo \"❌ Not available\")"
echo "  PDF Result: $([ \"$HTTP_STATUS\" = \"200\" ] && echo \"✅ Available\" || echo \"⚠️  Check status\")"

