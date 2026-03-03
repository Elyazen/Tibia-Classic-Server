#include "../src/common.hh"
#include <iostream>
#include <string>
#include <vector>
#include <cstring>

// Mock error function to avoid printing to stdout during tests if needed,
// or just let it print for now as we don't have a full test framework.
// Actually, src/utils.cc already defines it.

void test_is_countable() {
    std::cout << "Running test_is_countable..." << std::endl;
    struct TestCase {
        const char* input;
        bool expected;
    };

    std::vector<TestCase> cases = {
        {"some gold", false},
        {"a sword", true},
        {"an axe", true},
        {"apple", false},
        {"a ", true}, // minimal countable
        {"an ", true},
        {"some ", false}
    };

    for (const auto& c : cases) {
        bool result = IsCountable(c.input);
        if (result != c.expected) {
            std::cerr << "FAILED: IsCountable(\"" << c.input << "\") expected "
                      << c.expected << " but got " << result << std::endl;
            exit(1);
        }
    }
    std::cout << "test_is_countable passed!" << std::endl;
}

void test_plural() {
    std::cout << "Running test_plural..." << std::endl;
    struct TestCase {
        const char* s;
        int count;
        const char* expected;
    };

    std::vector<TestCase> cases = {
        // Count == 1 or not countable
        {"a sword", 1, "a sword"},
        {"some gold", 2, "some gold"},
        {"sword", 2, "sword"},

        // Count == 0 (In this implementation, it returns the plural name without the count)
        {"a sword", 0, "swords"},
        {"an axe", 0, "axes"},

        // Count > 1
        {"a sword", 2, "2 swords"},
        {"an axe", 3, "3 axes"},
        {"a knife", 2, "2 knives"},
        {"a throwing knife", 5, "5 throwing knives"},
        {"an orc spearman", 10, "10 orc spearmen"},
        {"a deer", 2, "2 deer"},
        {"a sheep", 3, "3 sheep"},
        {"a fish", 4, "4 fish"},
        {"a dead deer", 2, "2 dead deer"},
        {"a black sheep", 3, "3 black sheep"},

        // Suffix " of "
        {"a bag of gold", 2, "2 bags of gold"},
        {"a piece of cloth", 5, "5 pieces of cloth"},

        // Pluralization rules
        {"a bus", 2, "2 buses"},      // ends in 's'
        {"a box", 2, "2 boxes"},      // ends in 'x'
        {"a wish", 2, "2 wishes"},    // ends in 'sh'
        {"a watch", 2, "2 watches"},   // ends in 'ch'
        {"a city", 2, "2 cities"},    // ends in 'y' preceded by consonant
        {"a boy", 2, "2 boys"},      // ends in 'y' preceded by vowel
        {"a shelf", 2, "2 shelves"},  // ends in 'lf'
        {"a tomato", 2, "2 tomatoes"}, // ends in 'o'
        {"a book", 2, "2 books"},     // regular 's'

        // Negative count
        {"a sword", -1, "sword"} // Count < 0 returns ObjectNameString before pluralization and before adding count
    };

    for (const auto& c : cases) {
        const char* result = Plural(c.s, c.count);
        if (strcmp(result, c.expected) != 0) {
            std::cerr << "FAILED: Plural(\"" << (c.s ? c.s : "NULL") << "\", " << c.count
                      << ") expected \"" << c.expected << "\" but got \"" << result << "\"" << std::endl;
            exit(1);
        }
    }
    std::cout << "test_plural passed!" << std::endl;
}

int main() {
    test_is_countable();
    test_plural();
    std::cout << "All tests passed!" << std::endl;
    return 0;
}
