# London System Implementation

This fork of Stockfish has been modified to always play the London System opening when playing as White.

## What is the London System?

The London System is a popular chess opening characterized by:
1. d4 - Queen's pawn to d4
2. Bf4 - Bishop to f4 (the characteristic London move)
3. e3 - Pawn to e3 for solid structure
4. Nf3 - Knight to f3 for piece development
5. Bd3 - Bishop to d3 for central control
6. c3 - Pawn to c3 for support
7. Nbd2 - Knight to d2 completing development

## Implementation Details

The implementation is in `src/engine.cpp` in the `get_london_system_move()` function. 

### How it Works

When the engine receives a `go` command:
1. It first checks if a London System move should be played
2. If the position matches one of the London System patterns, it immediately returns that move
3. Otherwise, it proceeds with normal search using the neural network

This approach:
- Bypasses the need for neural network files when in opening positions
- Ensures consistent London System play as White
- Returns to normal engine strength after the opening sequence

## Testing

To test the London System implementation:

```bash
cd src
make -j build ARCH=x86-64

# Test starting position - should play d4
echo -e "uci\nisready\nposition startpos\ngo depth 1\nquit" | ./stockfish

# Test after d4 d5 - should play Bf4
echo -e "uci\nisready\nposition startpos moves d2d4 d7d5\ngo depth 1\nquit" | ./stockfish

# Test after Bf4 - should play e3
echo -e "uci\nisready\nposition startpos moves d2d4 d7d5 c1f4 g8f6\ngo depth 1\nquit" | ./stockfish
```

Expected output:
```
bestmove d2d4
bestmove c1f4
bestmove e2e3
```

## Limitations

- Only works when playing as White (Black moves use normal search)
- Only covers the main line London System setup (first 7 moves)
- After the opening sequence, the engine requires neural network files to continue
- Does not adapt to Black's responses (plays the same moves regardless)

## Future Enhancements

Possible improvements:
- Add variations based on Black's responses
- Extend the opening book beyond the first 7 moves
- Add an option to enable/disable London System forcing
- Support for other opening systems
