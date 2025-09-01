#include "crypto.hpp"

const uint8_t STATIC_KEY[16] = {
    0x55, 0x6E, 0x69, 0x74, 0x79, 0x46, 0x53, 0x00,
    0x00, 0x00, 0x00, 0x07, 0x35, 0x2E, 0x78, 0x2E
};
const size_t SIZE_FIELD_OFFSET = 0x1E;
const size_t XOR_MAX_SIZE = 0x8000;

void generate_xor_key(const uint8_t* header, uint8_t* xor_key) {
    for (int i = 0; i < 16; ++i)
        xor_key[i] = header[i] ^ STATIC_KEY[i];
}

void xor_buffer(uint8_t* buffer, size_t len, const uint8_t* key, size_t key_len, size_t offset) {
    for (size_t i = 0; i < len; ++i)
        buffer[i] ^= key[(i + offset) % key_len];
}

uint64_t read_big_endian_uint64(const uint8_t* bytes) {
    uint64_t value = 0;
    for (size_t i = 0; i < 8; ++i)
        value = (value << 8) | bytes[i];
    return value;
}

void process_memory_buffer(const uint8_t* data, size_t length, 
                           const std::string& base_name,
                           std::vector<std::pair<std::string, std::vector<uint8_t>>>& results,
                           int& sub_index,
                           std::ostringstream& log_str) 
{
    if (length < 38) {
        log_str << "Input too small: " << base_name << " at file index: " << sub_index << "\n";
        std::cerr << log_str.str();
        log_str.str("");
        return;
    }

    size_t remaining = length;

    // Header
    uint8_t header[16];
    std::memcpy(header, data, 16);

    uint8_t xor_key[16];
    generate_xor_key(header, xor_key);

    // File size
    uint8_t size_bytes[8];
    std::memcpy(size_bytes, data + SIZE_FIELD_OFFSET, 8);
    xor_buffer(size_bytes, 8, xor_key, 16, SIZE_FIELD_OFFSET);
    size_t file_size = read_big_endian_uint64(size_bytes);

    if (remaining < file_size) {
        log_str << "Error parsing file size: " << base_name << " at file index: " << sub_index << "\n";
        std::cerr << log_str.str();
        log_str.str("");
        return;
    }

    size_t xor_size = std::min(file_size, XOR_MAX_SIZE);

    // Prepare output buffer
    std::vector<uint8_t> out_buf(file_size);
    std::memcpy(out_buf.data(), data, file_size);

    // XOR first xor_size bytes
    xor_buffer(out_buf.data(), xor_size, xor_key, 16, 0);

    // Generate filename
    std::ostringstream name;
    name << base_name;
    if (sub_index > 1 || remaining > file_size)
        name << "_" << std::setfill('0') << std::setw(3) << sub_index;
    name << ".bundle";
    results.emplace_back(name.str(), std::move(out_buf));

    // Check for remainder
    remaining -= file_size;

    if (remaining > 0)
        process_memory_buffer(data + file_size, remaining, base_name, results, ++sub_index, log_str);
}
