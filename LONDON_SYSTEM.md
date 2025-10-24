# London System Implementation - Reward-Based Approach

This fork of Stockfish has been modified to encourage London System opening play when playing as White through a reward-based bonus system.

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

The implementation uses a **reward-based approach** rather than hardcoding specific moves. This is in `src/london.h` and integrated into `src/movepick.cpp`.

### How it Works

1. **Position Detection**: The `london_system_bonus()` function examines the current board position to identify London System opportunities
2. **Move Bonuses**: Assigns large bonuses (100,000 points) to moves that follow London System patterns
3. **Move Ordering**: These bonuses are applied during move ordering in the search algorithm
4. **Natural Search**: The engine still searches all legal moves and evaluates positions normally

### Key Advantages Over Hardcoding

- **Position-Aware**: Checks actual piece placement, not just move sequences
- **Flexible**: Works through Stockfish's natural search mechanism
- **Tactical**: Can deviate from London System if tactically necessary
- **Tunable**: Bonus values can be adjusted (currently hardcoded at 100,000)
- **UCI Option**: Includes `London_System_Bonus` option (not currently used, reserved for future enhancement)

## Current Behavior

The engine will **strongly prefer** London System moves in the opening because they receive massive bonuses that prioritize them in move ordering. However:

- The engine still evaluates all moves normally
- Can choose non-London moves if they are tactically superior
- Works best in typical opening positions
- Bonuses only apply to White's moves

## Testing

To test the London System influence:

```bash
cd src
make -j build ARCH=x86-64

# Test starting position
echo -e "uci\nisready\nposition startpos\ngo depth 10\nquit" | ./stockfish

# The engine should show preference for d4 and subsequent London moves
```

## UCI Options

- **London_System_Bonus**: Currently implemented but not active (default 0, range 0-10000)
  - Reserved for future use to make the bonus strength configurable
  - Currently bonuses are hardcoded in `london.h`

## Limitations

- Bonuses affect move **ordering**, not evaluation
- Very strong tactical positions may override London System preference  
- Only applies when playing as White
- Limited to the first 7 moves of London System
- Does not adapt to Black's specific responses

## Technical Implementation

**Files Modified:**
- `src/engine.cpp`: Added UCI option for London_System_Bonus
- `src/movepick.cpp`: Integrated bonus into move scoring for quiet moves
- `src/london.h`: New header with position-aware bonus calculation

The bonus is applied in the `score<QUIETS>()` function of MovePicker, which affects the order in which moves are searched during alpha-beta pruning.

## Future Enhancements

Possible improvements:
- Wire up UCI option to make bonus strength configurable at runtime
- Add response-dependent variations
- Extend beyond the first 7 moves
- Support for other opening systems
- Evaluation bonuses (not just move ordering)

