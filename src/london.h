/*
  Stockfish, a UCI chess playing engine derived from Glaurung 2.1
  Copyright (C) 2004-2025 The Stockfish developers (see AUTHORS file)

  Stockfish is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Stockfish is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef LONDON_H_INCLUDED
#define LONDON_H_INCLUDED

#include "position.h"
#include "types.h"

namespace Stockfish {

// Check if a move is part of the London System opening
// Returns a bonus score (0 if not a London System move)
inline int london_system_bonus(const Position& pos, Move m) {
    // Only apply bonus for White
    if (pos.side_to_move() != WHITE)
        return 0;

    Square from = m.from_sq();
    Square to   = m.to_sq();
    Piece  pc   = pos.moved_piece(m);

    // Check for London System moves
    Piece wPawn   = make_piece(WHITE, PAWN);
    Piece wKnight = make_piece(WHITE, KNIGHT);
    Piece wBishop = make_piece(WHITE, BISHOP);

    // Check piece positions for London System structure
    bool d2Pawn = (pos.piece_on(SQ_D2) == wPawn);
    bool d4Pawn = (pos.piece_on(SQ_D4) == wPawn);
    bool e2Pawn = (pos.piece_on(SQ_E2) == wPawn);
    bool e3Pawn = (pos.piece_on(SQ_E3) == wPawn);
    bool c2Pawn = (pos.piece_on(SQ_C2) == wPawn);
    bool c3Pawn = (pos.piece_on(SQ_C3) == wPawn);
    bool Bc1    = (pos.piece_on(SQ_C1) == wBishop);
    bool Bf4    = (pos.piece_on(SQ_F4) == wBishop);
    bool Bd3    = (pos.piece_on(SQ_D3) == wBishop);
    bool Ng1    = (pos.piece_on(SQ_G1) == wKnight);
    bool Nf3    = (pos.piece_on(SQ_F3) == wKnight);
    bool Nb1    = (pos.piece_on(SQ_B1) == wKnight);

    // 1. d2-d4: Opening move
    if (from == SQ_D2 && to == SQ_D4 && pc == wPawn && d2Pawn && e2Pawn && c2Pawn && Bc1
        && Ng1)
        return 100000;

    // 2. c1-f4: Characteristic London System bishop move
    if (from == SQ_C1 && to == SQ_F4 && pc == wBishop && d4Pawn && Bc1 && e2Pawn)
        return 100000;

    // 3. e2-e3: Solid pawn structure
    if (from == SQ_E2 && to == SQ_E3 && pc == wPawn && d4Pawn && Bf4 && e2Pawn)
        return 100000;

    // 4. g1-f3: Knight development
    if (from == SQ_G1 && to == SQ_F3 && pc == wKnight && d4Pawn && e3Pawn && Bf4 && Ng1)
        return 100000;

    // 5. f4-d3: Bishop to strong central square
    if (from == SQ_F4 && to == SQ_D3 && pc == wBishop && d4Pawn && e3Pawn && Nf3 && Bf4)
        return 100000;

    // 6. c2-c3: Pawn support
    if (from == SQ_C2 && to == SQ_C3 && pc == wPawn && d4Pawn && e3Pawn && Nf3 && Bd3
        && c2Pawn)
        return 100000;

    // 7. b1-d2: Knight to d2 completing development
    if (from == SQ_B1 && to == SQ_D2 && pc == wKnight && d4Pawn && e3Pawn && c3Pawn && Nf3
        && Bd3 && Nb1)
        return 100000;

    // Also give smaller bonuses for moves that maintain London System structure
    // when already in it
    if (d4Pawn && (Bf4 || Bd3)) {
        // We're in a London-like position, give small bonus to maintaining structure
        return 5000;
    }

    return 0;
}

}  // namespace Stockfish

#endif  // #ifndef LONDON_H_INCLUDED
