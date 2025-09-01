#include "file_io.hpp"

const uint8_t GFF_HEADER[4] = { 0x47, 0x46, 0x46, 0x00 };

void process_file(const fs::path& input_path, const fs::path& output_dir) {
    size_t length = fs::file_size(input_path);
    std::ifstream fin(input_path, std::ios::binary);
    std::ostringstream log_str;
    if (!fin) {
        log_str << "Failed to open: " << input_path << "\n";
        std::cerr << log_str.str();
        return;
    }

    // GFF check
    uint8_t magic[4];
    fin.read(reinterpret_cast<char*>(magic), 4);
    if (fin.gcount() < 4)
        return;
    if (std::memcmp(magic, GFF_HEADER, 4) == 0) {
        std::cout << "Skipped GFF file: " << input_path.filename() << "\n";
        return;
    }
    fin.clear();
    fin.seekg(0);

    // Read entire file into memory
    std::vector<uint8_t> file_data(length);
    fin.read(reinterpret_cast<char*>(file_data.data()), length);
    if ((size_t)fin.gcount() != length) {
        log_str << "Failed reading file: " << input_path.filename() << "\n";
        std::cerr << log_str.str();
        return;
    }

    // Process recursively in memory
    std::vector<std::pair<std::string, std::vector<uint8_t>>> results;
    int sub_index = 1;
    process_memory_buffer(file_data.data(), length, input_path.stem().string(), results, sub_index, log_str);

    // Write all output files sequentially
    for (auto& [fname, buf] : results) {
        fs::path out_path = output_dir / fname;
        std::ofstream fout(out_path, std::ios::binary);
        if (!fout) {
            log_str << "Failed to write: " << out_path << "\n";
            std::cerr << log_str.str();
            log_str.str("");
            continue;
        }
        fout.write(reinterpret_cast<char*>(buf.data()), buf.size());
    }
    size_t result_count = results.size();
    log_str << "Decrypted: " << input_path.filename().string();
    if (result_count > 1)
        log_str << " -> Split into " << result_count << " parts";
    log_str << "\n";
    std::cout << log_str.str();
}

void process_directory(const fs::path& input_dir, const fs::path& output_dir, bool parallel) {
    fs::create_directories(output_dir);
    
    std::vector<fs::path> files;
    for (auto& entry : fs::directory_iterator(input_dir)) {
        if (entry.is_regular_file() && entry.path().extension() == ".bundle")
            files.push_back(entry.path());
    }
    
    if (!parallel)
        for (auto& file : files)
            process_file(file, output_dir);
    else {
        size_t max_threads = std::min(std::thread::hardware_concurrency(), 4u);
        if (max_threads == 0)
            max_threads = 4;

        std::atomic<size_t> next_file(0);
        std::vector<std::future<void>> futures;

        auto worker = [&]() {
            while (true) {
                size_t idx = next_file.fetch_add(1);
                if (idx >= files.size())
                    break;
                process_file(files[idx], output_dir);
            }
        };

        for (size_t i = 0; i < max_threads; ++i)
            futures.emplace_back(std::async(std::launch::async, worker));

        for (auto& fut : futures)
            fut.get();
    }
}
