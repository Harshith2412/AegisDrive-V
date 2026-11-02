// minitest — a deliberately tiny, GoogleTest-SOURCE-COMPATIBLE fallback.
//
// WHY THIS EXISTS: the AegisDrive-V tests are written against GoogleTest and the
// CMake build fetches real GoogleTest. This header exists ONLY so the tests can be
// compiled and executed in environments without GoogleTest or network access
// (e.g. the sandbox where the initial vertical slice was developed).
// It supports only the subset of macros used in ecu/tests and emits a JSON report
// in a subset of GoogleTest's --gtest_output=json format.
// It is NOT a replacement for GoogleTest. Prefer the CMake build.
#pragma once
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <functional>
#include <iostream>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>

namespace minitest {
struct TestCase { std::string suite, name; std::function<void()> fn; };
inline std::vector<TestCase>& registry() { static std::vector<TestCase> r; return r; }
inline std::vector<std::string>*& current_failures() { static std::vector<std::string>* f = nullptr; return f; }
struct Registrar {
    Registrar(const char* s, const char* n, std::function<void()> fn) { registry().push_back({s, n, std::move(fn)}); }
};
struct FatalFailure {};
template <typename T, typename = void> struct printable : std::false_type {};
template <typename T>
struct printable<T, std::void_t<decltype(std::declval<std::ostream&>() << std::declval<const T&>())>> : std::true_type {};
template <typename T> std::string show(const T& v) {
    if constexpr (std::is_enum_v<T>) { return std::to_string(static_cast<long long>(v)); }
    else if constexpr (std::is_same_v<T, unsigned char> || std::is_same_v<T, signed char>) { return std::to_string(static_cast<int>(v)); }
    else if constexpr (printable<T>::value) { std::ostringstream o; o << v; return o.str(); }
    else { return "<unprintable>"; }
}
inline void fail(const char* file, int line, const std::string& msg, bool fatal) {
    std::ostringstream o; o << file << ":" << line << ": " << msg;
    if (current_failures()) current_failures()->push_back(o.str());
    std::cerr << "  FAILURE " << o.str() << "\n";
    if (fatal) throw FatalFailure{};
}
template <typename A, typename B, typename Op>
void cmp(const A& a, const B& b, Op op, const char* sa, const char* sb, const char* sop, const char* f, int l, bool fatal) {
    if (!op(a, b)) fail(f, l, std::string("Expected: ") + sa + " " + sop + " " + sb + " (" + show(a) + " vs " + show(b) + ")", fatal);
}
inline std::string json_escape(const std::string& s) {
    std::string o; for (char c : s) { if (c == '"' || c == '\\') { o += '\\'; o += c; } else if (c == '\n') o += "\\n"; else o += c; } return o;
}
inline int run_all(int argc, char** argv) {
    std::string json_path;
    for (int i = 1; i < argc; ++i) { const char* p = "--gtest_output=json:"; if (std::strncmp(argv[i], p, std::strlen(p)) == 0) json_path = argv[i] + std::strlen(p); }
    int failed = 0;
    std::ostringstream js; js << "{\"framework\":\"minitest-fallback\",\"testsuites\":[";
    std::string last_suite; bool first_suite = true, first_test = true;
    for (auto& t : registry()) {
        std::vector<std::string> fails; current_failures() = &fails;
        auto t0 = std::chrono::steady_clock::now();
        try { t.fn(); } catch (const FatalFailure&) {} catch (const std::exception& e) { fails.push_back(std::string("uncaught exception: ") + e.what()); }
        double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        current_failures() = nullptr;
        std::printf("[%s] %s.%s\n", fails.empty() ? "  OK  " : "FAILED", t.suite.c_str(), t.name.c_str());
        if (!fails.empty()) ++failed;
        if (t.suite != last_suite) { if (!first_suite) js << "]},"; js << "{\"name\":\"" << t.suite << "\",\"testsuite\":["; first_suite = false; first_test = true; last_suite = t.suite; }
        if (!first_test) { js << ","; }
        first_test = false;
        js << "{\"name\":\"" << t.name << "\",\"result\":\"COMPLETED\",\"time\":\"" << secs << "s\",\"failures\":[";
        for (size_t i = 0; i < fails.size(); ++i) js << (i ? "," : "") << "{\"failure\":\"" << json_escape(fails[i]) << "\"}";
        js << "]}";
    }
    if (!first_suite) js << "]}";
    js << "]}";
    std::printf("%zu tests, %d failed\n", registry().size(), failed);
    if (!json_path.empty()) { std::ofstream(json_path) << js.str(); }
    return failed ? 1 : 0;
}
}  // namespace minitest

namespace testing { inline void InitGoogleTest(int*, char**) {} }
#define RUN_ALL_TESTS() ::minitest::run_all(minitest_argc, minitest_argv)
#define TEST(S, N) \
    static void S##_##N##_impl(); \
    static ::minitest::Registrar S##_##N##_reg(#S, #N, &S##_##N##_impl); \
    static void S##_##N##_impl()
#define MT_CMP(a, b, op, sop, fatal) ::minitest::cmp((a), (b), [](const auto& x, const auto& y) { return x op y; }, #a, #b, sop, __FILE__, __LINE__, fatal)
#define EXPECT_EQ(a, b) MT_CMP(a, b, ==, "==", false)
#define EXPECT_NE(a, b) MT_CMP(a, b, !=, "!=", false)
#define EXPECT_LT(a, b) MT_CMP(a, b, <, "<", false)
#define EXPECT_LE(a, b) MT_CMP(a, b, <=, "<=", false)
#define EXPECT_GT(a, b) MT_CMP(a, b, >, ">", false)
#define EXPECT_GE(a, b) MT_CMP(a, b, >=, ">=", false)
#define ASSERT_EQ(a, b) MT_CMP(a, b, ==, "==", true)
#define ASSERT_TRUE(c) do { if (!(c)) ::minitest::fail(__FILE__, __LINE__, "Expected true: " #c, true); } while (0)
#define EXPECT_TRUE(c) do { if (!(c)) ::minitest::fail(__FILE__, __LINE__, "Expected true: " #c, false); } while (0)
#define EXPECT_FALSE(c) do { if (c) ::minitest::fail(__FILE__, __LINE__, "Expected false: " #c, false); } while (0)
#define EXPECT_NEAR(a, b, tol) do { double _a = (a), _b = (b); if (!(std::fabs(_a - _b) <= (tol))) ::minitest::fail(__FILE__, __LINE__, "Expected |" #a " - " #b "| <= " #tol " (" + std::to_string(_a) + " vs " + std::to_string(_b) + ")", false); } while (0)
