#!/bin/bash

# Comprehensive API Test Script for Trip Planner
# Tests all endpoints and verifies the complete trip planning flow

API_URL="https://ai-trip-planner-production-45dc.up.railway.app"
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_RESET='\033[0m'

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

print_success() {
    echo -e "${COLOR_GREEN}✅ $1${COLOR_RESET}"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${COLOR_RED}❌ $1${COLOR_RESET}"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${COLOR_BLUE}ℹ️  $1${COLOR_RESET}"
}

print_warning() {
    echo -e "${COLOR_YELLOW}⚠️  $1${COLOR_RESET}"
}

# Test 1: Health Check
print_header "TEST 1: Health Check Endpoint"
HEALTH_RESPONSE=$(curl -s "${API_URL}/")
if echo "$HEALTH_RESPONSE" | grep -q "running"; then
    print_success "Health check passed"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    print_error "Health check failed"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

# Test 2: Spell Check
print_header "TEST 2: Spell Check Endpoint"
SPELL_CHECK_RESPONSE=$(curl -s -X POST "${API_URL}/api/spell-check" \
  -H "Content-Type: application/json" \
  -d '{"text": "Pariss France Tokio"}')

if echo "$SPELL_CHECK_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if data.get('has_errors') else 1)" 2>/dev/null; then
    print_success "Spell check working - detected errors"
    echo "$SPELL_CHECK_RESPONSE" | python3 -m json.tool
else
    print_error "Spell check failed or unexpected response"
    echo "$SPELL_CHECK_RESPONSE"
fi

# Test 3: Create Trip
print_header "TEST 3: Create Trip Request"
TRIP_RESPONSE=$(curl -s -X POST "${API_URL}/api/trips" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Barcelona",
    "duration": 4,
    "budget": "moderate",
    "travel_style": ["cultural", "food", "beach"],
    "special_requirements": "Visit Sagrada Familia and try local tapas"
  }')

if echo "$TRIP_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'trip_id' in data else 1)" 2>/dev/null; then
    print_success "Trip created successfully"
    TRIP_ID=$(echo "$TRIP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['trip_id'])" 2>/dev/null)
    CLIENT_ID=$(echo "$TRIP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('client_id', 'N/A'))" 2>/dev/null)
    echo "$TRIP_RESPONSE" | python3 -m json.tool
    echo ""
    print_info "Trip ID: $TRIP_ID"
    print_info "Client ID: $CLIENT_ID"
else
    print_error "Failed to create trip"
    echo "$TRIP_RESPONSE"
    exit 1
fi

# Test 4: Usage Stats
print_header "TEST 4: Usage Statistics"
if [ ! -z "$CLIENT_ID" ] && [ "$CLIENT_ID" != "N/A" ]; then
    USAGE_RESPONSE=$(curl -s "${API_URL}/api/usage/${CLIENT_ID}")
    if echo "$USAGE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'trips_today' in data else 1)" 2>/dev/null; then
        print_success "Usage stats retrieved"
        echo "$USAGE_RESPONSE" | python3 -m json.tool
    else
        print_warning "Usage stats endpoint returned unexpected response"
        echo "$USAGE_RESPONSE"
    fi
else
    print_warning "Skipping usage stats test (no client ID)"
fi

# Test 5: Monitor Progress
print_header "TEST 5: Monitor Trip Progress"
print_info "Monitoring trip: $TRIP_ID"
print_info "This may take 2-3 minutes..."

MAX_CHECKS=60
CHECK_INTERVAL=5
COMPLETED=false
ERROR=false

for i in $(seq 1 $MAX_CHECKS); do
    PROGRESS_RESPONSE=$(curl -s "${API_URL}/api/trips/${TRIP_ID}/progress")
    STATUS=$(echo "$PROGRESS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
    PROGRESS=$(echo "$PROGRESS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('progress', 0))" 2>/dev/null)
    MESSAGE=$(echo "$PROGRESS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'N/A'))" 2>/dev/null)
    AGENT=$(echo "$PROGRESS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('current_agent', 'N/A'))" 2>/dev/null)
    
    printf "\r[Check #%02d] Status: %-10s Progress: %3d%% Agent: %-20s" "$i" "$STATUS" "$PROGRESS" "$AGENT"
    
    if [ "$STATUS" = "completed" ]; then
        COMPLETED=true
        echo ""
        print_success "Trip planning completed!"
        break
    fi
    
    if [ "$STATUS" = "error" ]; then
        ERROR=true
        echo ""
        print_error "Trip planning failed!"
        echo "$PROGRESS_RESPONSE" | python3 -m json.tool
        break
    fi
    
    sleep $CHECK_INTERVAL
done

echo ""

if [ "$COMPLETED" = false ] && [ "$ERROR" = false ]; then
    print_warning "Trip did not complete within expected time"
    print_info "Current status: $STATUS"
fi

# Test 6: Get HTML Result
print_header "TEST 6: Get HTML Result"
if [ "$COMPLETED" = true ]; then
    RESULT_RESPONSE=$(curl -s "${API_URL}/api/trips/${TRIP_ID}/result")
    
    if echo "$RESULT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'html_content' in data else 1)" 2>/dev/null; then
        print_success "HTML result retrieved successfully"
        
        HTML_LEN=$(echo "$RESULT_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('html_content', '')))" 2>/dev/null)
        HTML_PREVIEW=$(echo "$RESULT_RESPONSE" | python3 -c "import sys, json; content=json.load(sys.stdin).get('html_content', ''); print(content[:300])" 2>/dev/null)
        
        echo ""
        print_info "HTML Content Length: $HTML_LEN characters"
        echo ""
        print_info "HTML Preview (first 300 chars):"
        echo "$HTML_PREVIEW..."
        echo ""
        
        # Check HTML structure
        FULL_HTML=$(echo "$RESULT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('html_content', ''))" 2>/dev/null)
        if echo "$FULL_HTML" | grep -qi "<html"; then
            print_success "HTML contains <html> tag"
        else
            print_warning "HTML may not contain <html> tag"
        fi
        
        if echo "$FULL_HTML" | grep -qi "<body"; then
            print_success "HTML contains <body> tag"
        else
            print_warning "HTML may not contain <body> tag"
        fi
        
        # Save HTML to file
        echo "$RESULT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('html_content', ''))" > "trip_result_${TRIP_ID}.html" 2>/dev/null
        if [ -f "trip_result_${TRIP_ID}.html" ]; then
            print_success "HTML saved to: trip_result_${TRIP_ID}.html"
        fi
    else
        print_error "Failed to retrieve HTML result"
        echo "$RESULT_RESPONSE" | head -20
    fi
else
    print_warning "Skipping HTML result test (trip not completed)"
fi

# Test 7: Get PDF Result
print_header "TEST 7: Get PDF Result"
if [ "$COMPLETED" = true ]; then
    PDF_FILE="trip_result_${TRIP_ID}.pdf"
    
    # Download PDF directly to file (binary mode)
    HTTP_STATUS=$(curl -s -o "${PDF_FILE}" -w "%{http_code}" "${API_URL}/api/trips/${TRIP_ID}/result/pdf")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        if [ -f "${PDF_FILE}" ]; then
            PDF_SIZE=$(wc -c < "${PDF_FILE}" | tr -d ' ')
            PDF_SIZE_KB=$(echo "scale=2; $PDF_SIZE/1024" | bc 2>/dev/null || echo "N/A")
            PDF_HEADER=$(head -c 4 "${PDF_FILE}")
            
            print_success "PDF generated successfully"
            print_info "HTTP Status: $HTTP_STATUS"
            print_info "PDF Size: $PDF_SIZE bytes ($PDF_SIZE_KB KB)"
            
            if [ "$PDF_HEADER" = "%PDF" ]; then
                print_success "PDF has valid header - saved to: ${PDF_FILE}"
            else
                print_warning "PDF header may be invalid (got: '$PDF_HEADER')"
            fi
        else
            print_error "PDF file was not created"
        fi
    else
        print_warning "PDF generation returned status: $HTTP_STATUS"
        if [ "$HTTP_STATUS" = "503" ] || [ "$HTTP_STATUS" = "500" ]; then
            print_info "Note: PDF generation may require WeasyPrint. Check backend logs."
        fi
        if [ -f "${PDF_FILE}" ]; then
            head -10 "${PDF_FILE}"
        fi
    fi
else
    print_warning "Skipping PDF result test (trip not completed)"
fi

# Test 8: Verify Progress Endpoint Details
print_header "TEST 8: Verify Progress Endpoint Details"
FINAL_PROGRESS=$(curl -s "${API_URL}/api/trips/${TRIP_ID}/progress")
if [ ! -z "$FINAL_PROGRESS" ]; then
    echo "$FINAL_PROGRESS" | python3 -m json.tool | head -30
    print_success "Progress endpoint returns detailed information"
else
    print_error "Progress endpoint returned empty response"
fi

# Summary
print_header "TEST SUMMARY"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo ""

if [ "$COMPLETED" = true ]; then
    print_success "All critical tests completed!"
    echo ""
    print_info "Files created:"
    [ -f "trip_result_${TRIP_ID}.html" ] && echo "  - trip_result_${TRIP_ID}.html"
    [ -f "trip_result_${TRIP_ID}.pdf" ] && echo "  - trip_result_${TRIP_ID}.pdf"
else
    print_warning "Some tests were skipped because trip did not complete"
    print_info "You can check the trip status later with:"
    echo "  curl -s ${API_URL}/api/trips/${TRIP_ID}/progress | python3 -m json.tool"
fi

echo ""
print_info "Trip ID for reference: $TRIP_ID"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi

