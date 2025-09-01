#pragma once

#include <atomic>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <future>
#include <iostream>
#include <thread>
#include <vector>

#include "crypto.hpp"

namespace fs = std::filesystem;

void process_file(const fs::path& input_path, const fs::path& output_dir);
void process_directory(const fs::path& input_dir, const fs::path& output_dir, bool parallel);
