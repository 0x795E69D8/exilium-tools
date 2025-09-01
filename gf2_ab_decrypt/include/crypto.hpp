#pragma once

#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>

void generate_xor_key(const uint8_t* header, uint8_t* xor_key);
void xor_buffer(uint8_t* buffer, size_t len, const uint8_t* key, size_t key_len, size_t offset);
uint64_t read_big_endian_uint64(const uint8_t* bytes);
void process_memory_buffer(const uint8_t* data, size_t length, 
                           const std::string& base_name,
                           std::vector<std::pair<std::string, std::vector<uint8_t>>>& results,
                           int& sub_index,
                           std::ostringstream& log_str);
