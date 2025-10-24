#!/bin/bash
# Test script for London System implementation
# This script tests that Stockfish plays London System moves as White

echo "Testing London System Implementation"
echo "====================================="
echo ""

cd src

if [ ! -f stockfish ]; then
    echo "Error: stockfish executable not found. Please run 'make build' first."
    exit 1
fi

echo "Test 1: Starting position should play d4"
result=$(echo -e "uci\nisready\nposition startpos\ngo depth 1\nquit" | timeout 2 ./stockfish 2>&1 | grep "bestmove")
echo "$result"
if [[ $result == *"d2d4"* ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi
echo ""

echo "Test 2: After d4 d5, should play Bf4"
result=$(echo -e "uci\nisready\nposition startpos moves d2d4 d7d5\ngo depth 1\nquit" | timeout 2 ./stockfish 2>&1 | grep "bestmove")
echo "$result"
if [[ $result == *"c1f4"* ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi
echo ""

echo "Test 3: After d4 d5 Bf4 Nf6, should play e3"
result=$(echo -e "uci\nisready\nposition startpos moves d2d4 d7d5 c1f4 g8f6\ngo depth 1\nquit" | timeout 2 ./stockfish 2>&1 | grep "bestmove")
echo "$result"
if [[ $result == *"e2e3"* ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi
echo ""

echo "Test 4: After d4 d5 Bf4 Nf6 e3 e6, should play Nf3"
result=$(echo -e "uci\nisready\nposition startpos moves d2d4 d7d5 c1f4 g8f6 e2e3 e7e6\ngo depth 1\nquit" | timeout 2 ./stockfish 2>&1 | grep "bestmove")
echo "$result"
if [[ $result == *"g1f3"* ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi
echo ""

echo "Test 5: After d4 d5 Bf4 Nf6 e3 e6 Nf3 c5, should play Bd3"
result=$(echo -e "uci\nisready\nposition startpos moves d2d4 d7d5 c1f4 g8f6 e2e3 e7e6 g1f3 c7c5\ngo depth 1\nquit" | timeout 2 ./stockfish 2>&1 | grep "bestmove")
echo "$result"
if [[ $result == *"f4d3"* ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi
echo ""

echo "====================================="
echo "All tests passed! ✓"
echo "London System implementation is working correctly."
