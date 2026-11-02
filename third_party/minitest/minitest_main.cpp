// Entry point for the minitest fallback (real GoogleTest builds link gtest_main instead).
#include "gtest/gtest.h"
int main(int minitest_argc, char** minitest_argv) {
    testing::InitGoogleTest(&minitest_argc, minitest_argv);
    return RUN_ALL_TESTS();
}
