#include <chrono>
#include <cstring>
#include <filesystem>
#include <iostream>

#include "file_io.hpp"
#include "verify.hpp"

namespace fs = std::filesystem;

int main(int argc, char* argv[]) {
    fs::path p(argv[0]);
    if (argc < 2) {
        std::cerr << "Usage: \"" << p.filename().string() << " <input_dir> [--out <output_dir>] [--parallel] [--verify]\" or \"" << p.filename().string() << " <input_dir> --verify-only\"\n";
        return 1;
    }

    fs::path input_folder = argv[1];
    fs::path output_folder = "./AssetBundles_Decrypted";
    bool custom_out = false, do_parallel = false, do_verify = false, verify_only = false;
    
    for (int i = 2; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--out" && i + 1 < argc) {
            custom_out = true; output_folder = argv[++i];
        }
        else if (arg == "--parallel")
            do_parallel = true;
        else if (arg == "--verify")
            do_verify = true;
        else if (arg == "--verify-only")
            verify_only = true;
        else {
            std::cerr << "Unknown option: " << arg << "\n";
            return 1;
        }
    }

    if (!fs::exists(input_folder) || !fs::is_directory(input_folder)) {
        std::cerr << "Input folder does not exist or is not a directory.\n";
        return 1;
    }
    
    if (verify_only && (custom_out || do_parallel || do_verify)) {
        std::cerr << "Can't use --verify-only with other options\n";
        return 1;
    }
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    if (verify_only) {
        std::cout << "Verifying files... (this might take a while)\n";
        verify(input_folder);
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now() - start_time).count();
        std::cout << "Verification duration: " << duration / 1000.0 << " seconds (" << duration << " ms)\n";
        return 0;
    }

    process_directory(input_folder, output_folder, do_parallel);
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now() - start_time).count();
    std::cout << "Decryption duration: " << duration / 1000.0 << " seconds (" << duration << " ms)\n";

    if (do_verify) {
        start_time = std::chrono::high_resolution_clock::now();
        std::cout << "Verifying output files... (this might take a while)\n";
        verify(output_folder);
        duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now() - start_time).count();
        std::cout << "Verification duration: " << duration / 1000.0 << " seconds (" << duration << " ms)\n";
    }
    
    return 0;
}
