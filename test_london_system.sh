#!/bin/bash
# Test script for London System implementation
# This script tests that Stockfish plays London System moves as White

set -e  # Exit on error

TIMEOUT=5  # Timeout in seconds for each test

echo "Testing London System Implementation"
echo "====================================="
echo ""

cd src

if [ ! -f stockfish ]; then
    echo "Error: stockfish executable not found. Please run 'make build' first."
    exit 1
fi

# Helper function to run a test
run_test() {
    local test_name="$1"
    local position="$2"
    local expected_move="$3"
    
    echo "Test: $test_name"
    
    # Run the engine and capture output
    result=$(echo -e "uci\nisready\n$position\ngo depth 1\nquit" | timeout "$TIMEOUT" ./stockfish 2>&1 | grep "bestmove" || true)
    
    # Check if we got a result
    if [ -z "$result" ]; then
        echo "✗ FAIL - No output received (timeout or error)"
        return 1
    fi
    
    echo "$result"
    
    # Check if the expected move is in the result
    if [[ $result == *"$expected_move"* ]]; then
        echo "✓ PASS"
        return 0
    else
        echo "✗ FAIL - Expected move '$expected_move' not found"
        return 1
    fi
}

# Run tests
failed=0

run_test "Starting position should play d4" "position startpos" "d2d4" || failed=$((failed+1))
echo ""

run_test "After d4 d5, should play Bf4" "position startpos moves d2d4 d7d5" "c1f4" || failed=$((failed+1))
echo ""

run_test "After d4 d5 Bf4 Nf6, should play e3" "position startpos moves d2d4 d7d5 c1f4 g8f6" "e2e3" || failed=$((failed+1))
echo ""

run_test "After d4 d5 Bf4 Nf6 e3 e6, should play Nf3" "position startpos moves d2d4 d7d5 c1f4 g8f6 e2e3 e7e6" "g1f3" || failed=$((failed+1))
echo ""

run_test "After d4 d5 Bf4 Nf6 e3 e6 Nf3 c5, should play Bd3" "position startpos moves d2d4 d7d5 c1f4 g8f6 e2e3 e7e6 g1f3 c7c5" "f4d3" || failed=$((failed+1))
echo ""

# Summary
echo "====================================="
if [ $failed -eq 0 ]; then
    echo "All tests passed! ✓"
    echo "London System implementation is working correctly."
    exit 0
else
    echo "$failed test(s) failed! ✗"
    exit 1
fi
