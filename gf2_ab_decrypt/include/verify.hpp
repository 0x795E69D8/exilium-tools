#pragma once

#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>

#include "crypto.hpp"

namespace fs = std::filesystem;

void verify(const fs::path& dir);
