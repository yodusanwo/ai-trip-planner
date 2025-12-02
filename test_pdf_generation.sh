#!/bin/bash

# Quick test script to create a trip and immediately test PDF generation
API_URL="https://ai-trip-planner-production-45dc.up.railway.app"

echo "=== Testing PDF Generation ==="
echo ""

# Step 1: Create a trip
echo "1. Creating trip..."
TRIP_RESPONSE=$(curl -s -X POST "${API_URL}/api/trips" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Barcelona",
    "duration": 3,
    "budget": "moderate",
    "travel_style": ["cultural"],
    "special_requirements": ""
  }')

TRIP_ID=$(echo "$TRIP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['trip_id'])" 2>/dev/null)
echo "Trip ID: $TRIP_ID"
echo ""

# Step 2: Monitor until complete
echo "2. Monitoring trip progress..."
MAX_CHECKS=60
for i in $(seq 1 $MAX_CHECKS); do
    PROGRESS=$(curl -s "${API_URL}/api/trips/${TRIP_ID}/progress")
    STATUS=$(echo "$PROGRESS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    PROGRESS_PCT=$(echo "$PROGRESS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('progress', 0))" 2>/dev/null)
    
    printf "\r[%02d] Status: %-10s Progress: %3d%%" "$i" "$STATUS" "$PROGRESS_PCT"
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "✅ Trip completed!"
        break
    fi
    
    if [ "$STATUS" = "error" ]; then
        echo ""
        echo "❌ Trip failed!"
        exit 1
    fi
    
    sleep 5
done

echo ""
echo ""

# Step 3: Test HTML result
echo "3. Testing HTML result..."
HTML_RESPONSE=$(curl -s "${API_URL}/api/trips/${TRIP_ID}/result")
HTML_LEN=$(echo "$HTML_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('html_content', '')))" 2>/dev/null)

if [ "$HTML_LEN" -gt 100 ]; then
    echo "✅ HTML result available ($HTML_LEN characters)"
else
    echo "❌ HTML result not available"
    exit 1
fi

# Step 4: Test PDF generation immediately
echo ""
echo "4. Testing PDF generation..."
PDF_FILE="test_pdf_${TRIP_ID}.pdf"

# Download PDF directly to file (binary mode)
HTTP_STATUS=$(curl -s -o "${PDF_FILE}" -w "%{http_code}" "${API_URL}/api/trips/${TRIP_ID}/result/pdf")

if [ "$HTTP_STATUS" = "200" ]; then
    if [ -f "${PDF_FILE}" ]; then
        PDF_SIZE=$(wc -c < "${PDF_FILE}" | tr -d ' ')
        PDF_HEADER=$(head -c 4 "${PDF_FILE}")
        
        echo "✅ PDF endpoint returned 200"
        echo "   PDF Size: $PDF_SIZE bytes"
        echo "   PDF Header: $PDF_HEADER"
        
        if [ "$PDF_HEADER" = "%PDF" ]; then
            echo "✅ PDF has valid header!"
            echo "✅ PDF saved to: ${PDF_FILE}"
        else
            echo "❌ PDF header invalid (should be '%PDF', got: '$PDF_HEADER')"
            echo "First 50 bytes:"
            head -c 50 "${PDF_FILE}" | od -c | head -3
        fi
    else
        echo "❌ PDF file was not created"
    fi
else
    echo "❌ PDF endpoint returned: $HTTP_STATUS"
    if [ -f "${PDF_FILE}" ]; then
        echo "Response content:"
        head -20 "${PDF_FILE}"
    fi
fi

echo ""
echo "=== Test Complete ==="

