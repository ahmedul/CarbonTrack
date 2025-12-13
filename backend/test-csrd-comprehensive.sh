#!/bin/bash
# Comprehensive CSRD API Testing Script
# Tests all 19 CSRD endpoints in production

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API Configuration
API_URL="https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod"
CSRD_BASE="${API_URL}/api/v1/csrd"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Helper functions
print_test() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}TEST $1: $2${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✓ PASSED${NC}: $1"
    echo ""
}

print_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}✗ FAILED${NC}: $1"
    echo -e "${RED}Error:${NC} $2"
    echo ""
}

# Test authentication (needs valid token)
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     CSRD API Comprehensive Testing Suite                 ║"
echo "║     Production Environment: eu-central-1                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Prompt for authentication token
echo -e "${YELLOW}Enter your JWT token (or press Enter to use demo token):${NC}"
read -r AUTH_TOKEN

if [ -z "$AUTH_TOKEN" ]; then
    AUTH_TOKEN="demo-token-12345"
    echo -e "${YELLOW}Using demo token (may not have CSRD access)${NC}"
fi

echo ""

# =============================================================================
# TEST 1: Health Check
# =============================================================================
print_test "1" "Health Check - GET /health"
TESTS_TOTAL=$((TESTS_TOTAL + 1))

RESPONSE=$(curl -s -w "\n%{http_code}" "${API_URL}/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "Response: $BODY"
    print_pass "Health check successful"
else
    print_fail "Health check failed" "HTTP $HTTP_CODE"
fi

# =============================================================================
# TEST 2: Create CSRD Report
# =============================================================================
print_test "2" "Create Report - POST /csrd/reports"
TESTS_TOTAL=$((TESTS_TOTAL + 1))

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${CSRD_BASE}/reports" \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "company_name=Test Company GmbH" \
    -d "reporting_year=2025" \
    -d "country=DE" \
    -d "employee_count=350" \
    -d "annual_revenue_eur=75000000" \
    -d "reporting_period=ANNUAL")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 201 ] || [ "$HTTP_CODE" -eq 200 ]; then
    REPORT_ID=$(echo "$BODY" | grep -o '"report_id":"[^"]*"' | cut -d'"' -f4)
    echo "Created Report ID: $REPORT_ID"
    echo "Response: $BODY" | head -c 500
    print_pass "Report created successfully"
else
    print_fail "Report creation failed" "HTTP $HTTP_CODE - $BODY"
    REPORT_ID=""
fi

# =============================================================================
# TEST 3: List All Reports
# =============================================================================
print_test "3" "List Reports - GET /csrd/reports"
TESTS_TOTAL=$((TESTS_TOTAL + 1))

RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/reports" \
    -H "Authorization: Bearer ${AUTH_TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    COUNT=$(echo "$BODY" | grep -o '"total":' | wc -l)
    echo "Response: $BODY" | head -c 500
    print_pass "Retrieved reports list (found entries)"
else
    print_fail "List reports failed" "HTTP $HTTP_CODE"
fi

# =============================================================================
# TEST 4: Get Specific Report
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "4" "Get Report Details - GET /csrd/reports/{id}"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/reports/${REPORT_ID}" \
        -H "Authorization: Bearer ${AUTH_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "Retrieved report details"
    else
        print_fail "Get report failed" "HTTP $HTTP_CODE"
    fi
fi

# =============================================================================
# TEST 5: Update Report
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "5" "Update Report - PUT /csrd/reports/{id}"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "${CSRD_BASE}/reports/${REPORT_ID}" \
        -H "Authorization: Bearer ${AUTH_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "status": "IN_PROGRESS",
            "employee_count": 380
        }')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "Report updated successfully"
    else
        print_fail "Update report failed" "HTTP $HTTP_CODE - $BODY"
    fi
fi

# =============================================================================
# TEST 6: Add Emissions Data
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "6" "Add Emissions - POST /csrd/reports/{id}/emissions"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${CSRD_BASE}/reports/${REPORT_ID}/emissions" \
        -H "Authorization: Bearer ${AUTH_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "scope_1": 5000.5,
            "scope_2": 3200.75,
            "scope_3": 12000.0,
            "biogenic": 150.25
        }')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "Emissions data added"
    else
        print_fail "Add emissions failed" "HTTP $HTTP_CODE - $BODY"
    fi
fi

# =============================================================================
# TEST 7: Get Standards for Report
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "7" "Get Standards - GET /csrd/reports/{id}/standards"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/reports/${REPORT_ID}/standards" \
        -H "Authorization: Bearer ${AUTH_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "Retrieved ESRS standards"
    else
        print_fail "Get standards failed" "HTTP $HTTP_CODE"
    fi
fi

# =============================================================================
# TEST 8: Get Specific Standard Details
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "8" "Get Standard E1 - GET /csrd/reports/{id}/standards/E1"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/reports/${REPORT_ID}/standards/E1" \
        -H "Authorization: Bearer ${AUTH_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "Retrieved E1 (Climate Change) standard"
    else
        print_fail "Get E1 standard failed" "HTTP $HTTP_CODE"
    fi
fi

# =============================================================================
# TEST 9: Update Metric
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "9" "Update Metric - PUT /csrd/reports/{id}/standards/E1/metrics/ghg_emissions"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "${CSRD_BASE}/reports/${REPORT_ID}/standards/E1/metrics/ghg_emissions" \
        -H "Authorization: Bearer ${AUTH_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "value": 20351.5,
            "unit": "tCO2e",
            "verified": false
        }')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "Metric updated successfully"
    else
        print_fail "Update metric failed" "HTTP $HTTP_CODE - $BODY"
    fi
fi

# =============================================================================
# TEST 10: Validate Compliance
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "10" "Validate Compliance - GET /csrd/reports/{id}/validate"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/reports/${REPORT_ID}/validate" \
        -H "Authorization: Bearer ${AUTH_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "Validation completed"
    else
        print_fail "Validation failed" "HTTP $HTTP_CODE"
    fi
fi

# =============================================================================
# TEST 11: Generate PDF
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "11" "Generate PDF - POST /csrd/reports/{id}/generate-pdf"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${CSRD_BASE}/reports/${REPORT_ID}/generate-pdf" \
        -H "Authorization: Bearer ${AUTH_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "PDF generation initiated"
    else
        print_fail "PDF generation failed" "HTTP $HTTP_CODE - $BODY"
    fi
fi

# =============================================================================
# TEST 12: Export XBRL
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "12" "Export XBRL - GET /csrd/reports/{id}/xbrl"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/reports/${REPORT_ID}/xbrl" \
        -H "Authorization: Bearer ${AUTH_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "XBRL export successful"
    else
        print_fail "XBRL export failed" "HTTP $HTTP_CODE - $BODY"
    fi
fi

# =============================================================================
# TEST 13: Get Audit Trail
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    print_test "13" "Get Audit Trail - GET /csrd/audit-trail/{report_id}"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/audit-trail/${REPORT_ID}" \
        -H "Authorization: Bearer ${AUTH_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "Response: $BODY" | head -c 500
        print_pass "Audit trail retrieved"
    else
        print_fail "Get audit trail failed" "HTTP $HTTP_CODE"
    fi
fi

# =============================================================================
# TEST 14: Get Metrics History
# =============================================================================
print_test "14" "Get Metrics History - GET /csrd/metrics/history"
TESTS_TOTAL=$((TESTS_TOTAL + 1))

RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/metrics/history?company_id=test-company&start_date=2024-01-01&end_date=2025-12-31" \
    -H "Authorization: Bearer ${AUTH_TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "Response: $BODY" | head -c 500
    print_pass "Metrics history retrieved"
else
    print_fail "Get metrics history failed" "HTTP $HTTP_CODE"
fi

# =============================================================================
# TEST 15: Compare Reports
# =============================================================================
print_test "15" "Compare Reports - GET /csrd/reports/compare"
TESTS_TOTAL=$((TESTS_TOTAL + 1))

RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/reports/compare?report_id_1=${REPORT_ID}&report_id_2=${REPORT_ID}" \
    -H "Authorization: Bearer ${AUTH_TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "Response: $BODY" | head -c 500
    print_pass "Report comparison completed"
else
    print_fail "Compare reports failed" "HTTP $HTTP_CODE - $BODY"
fi

# =============================================================================
# TEST 16: List Available Standards
# =============================================================================
print_test "16" "List Standards - GET /csrd/standards"
TESTS_TOTAL=$((TESTS_TOTAL + 1))

RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/standards" \
    -H "Authorization: Bearer ${AUTH_TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "Response: $BODY" | head -c 500
    print_pass "Standards list retrieved"
else
    print_fail "List standards failed" "HTTP $HTTP_CODE"
fi

# =============================================================================
# TEST 17: Filter Reports by Year
# =============================================================================
print_test "17" "Filter by Year - GET /csrd/reports?year=2025"
TESTS_TOTAL=$((TESTS_TOTAL + 1))

RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/reports?year=2025" \
    -H "Authorization: Bearer ${AUTH_TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "Response: $BODY" | head -c 500
    print_pass "Filtered reports by year"
else
    print_fail "Filter by year failed" "HTTP $HTTP_CODE"
fi

# =============================================================================
# TEST 18: Filter Reports by Status
# =============================================================================
print_test "18" "Filter by Status - GET /csrd/reports?status=IN_PROGRESS"
TESTS_TOTAL=$((TESTS_TOTAL + 1))

RESPONSE=$(curl -s -w "\n%{http_code}" "${CSRD_BASE}/reports?status=IN_PROGRESS" \
    -H "Authorization: Bearer ${AUTH_TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "Response: $BODY" | head -c 500
    print_pass "Filtered reports by status"
else
    print_fail "Filter by status failed" "HTTP $HTTP_CODE"
fi

# =============================================================================
# TEST 19: Delete Report (Optional - cleanup)
# =============================================================================
if [ -n "$REPORT_ID" ]; then
    echo -e "${YELLOW}Do you want to delete the test report? (y/N)${NC}"
    read -r DELETE_CONFIRM
    
    if [ "$DELETE_CONFIRM" = "y" ] || [ "$DELETE_CONFIRM" = "Y" ]; then
        print_test "19" "Delete Report - DELETE /csrd/reports/{id}"
        TESTS_TOTAL=$((TESTS_TOTAL + 1))
        
        RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${CSRD_BASE}/reports/${REPORT_ID}" \
            -H "Authorization: Bearer ${AUTH_TOKEN}")
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | sed '$d')
        
        if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 204 ]; then
            print_pass "Report deleted successfully"
        else
            print_fail "Delete report failed" "HTTP $HTTP_CODE - $BODY"
        fi
    else
        echo -e "${YELLOW}Skipping delete - test report preserved${NC}"
    fi
fi

# =============================================================================
# TEST SUMMARY
# =============================================================================
echo ""
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                   TEST SUMMARY                            ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "Total Tests:  ${TESTS_TOTAL}"
echo -e "${GREEN}Passed:       ${TESTS_PASSED}${NC}"
echo -e "${RED}Failed:       ${TESTS_FAILED}${NC}"

PASS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))
echo -e "Pass Rate:    ${PASS_RATE}%"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed! CSRD API is fully functional.${NC}\n"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed. Please review the errors above.${NC}\n"
    exit 1
fi
