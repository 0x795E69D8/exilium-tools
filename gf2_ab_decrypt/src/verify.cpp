#include "verify.hpp"

const uint8_t UNITY_AB_HEADER[30] = {
    0x55, 0x6E, 0x69, 0x74, 0x79, 0x46, 0x53, 0x00,
    0x00, 0x00, 0x00, 0x07, 0x35, 0x2E, 0x78, 0x2E,
    0x78, 0x00, 0x32, 0x30, 0x31, 0x39, 0x2E, 0x34,
    0x2E, 0x32, 0x39, 0x66, 0x31, 0x00
};

void verify(const fs::path& dir) {
    int verified_count = 0;
    for (auto& entry : fs::directory_iterator(dir)) {
        if (!entry.is_regular_file() || entry.path().extension() != ".bundle")
            continue;

        std::ifstream fin(entry.path(), std::ios::binary);
        if (!fin) {
            std::cerr << "Verification failed: Failed to open " << entry.path().filename() << "\n";
            continue;
        }

        uint8_t header[38];
        fin.read(reinterpret_cast<char*>(header), 38);
        if (fin.gcount() < 38) {
            std::cerr << "Verification failed: File too small " << entry.path().filename() << "\n";
            continue;
        }
        if (std::memcmp(header, UNITY_AB_HEADER, 30) != 0) {
            std::cerr << "Verification failed: Incorrect Unity Asset Bundle header " << entry.path().filename() << "\n";
            continue;
        }

        size_t declared_size = read_big_endian_uint64(header + 30);
        size_t actual_size = fs::file_size(entry.path());
        if (declared_size != actual_size) {
            std::cerr << "Verification failed: Size mismatch in " << entry.path().filename()
                      << " (declared " << declared_size << ", actual " << actual_size << ")\n";
            continue;
        }
        verified_count++;
    }
    std::cout << "Verification passed: " << verified_count << " files\n";
}
