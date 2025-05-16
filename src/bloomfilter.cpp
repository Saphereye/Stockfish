#include "bloomfilter.h"

namespace Stockfish {
BloomFilter::BloomFilter() :
    bitset() {}

void BloomFilter::insert(const Key& key) const {
    const auto hash1 = uint64_t(key);
    const auto hash2 = uint64_t(key >> 16);

    for (auto i = 0; i < NO_OF_HASH_FUNCTIONS; ++i)
    {
        const int hash = (hash1 + i * hash2) % CAPACITY;
        bitset.set(hash);
    }
}

bool BloomFilter::contains(const Key& key) const {
    const auto hash1 = uint64_t(key);
    const auto hash2 = uint64_t(key >> 16);

    for (auto i = 0; i < NO_OF_HASH_FUNCTIONS; ++i)
    {
        const int hash = (hash1 + i * hash2) % CAPACITY;
        if (!bitset.test(hash))
        {
            return false;
        }
    }
    return true;
}

void BloomFilter::clear() { bitset.reset(); }
}  // namespace Stockfish
