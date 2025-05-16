#ifndef BLOOMFILTER_H_INCLUDED
#define BLOOMFILTER_H_INCLUDED
#include "memory.h"
#include <bitset>
#include <cmath>
#include <cstddef>

const auto CAPACITY             = 9'585'059;
const auto NO_OF_HASH_FUNCTIONS = 7;

namespace Stockfish {
class BloomFilter {
   public:
    BloomFilter();
    void insert(const Key& key) const;
    bool contains(const Key& key) const;
    void clear();

   private:
    mutable std::bitset<CAPACITY> bitset;
};
}  // namespace Stockfish

#endif  // #ifndef BLOOMFILTER_H_INCLUDED
