# Girls' Frontline 2 Asset Bundle Decryption

## Features

- 🔑 Decrypts *Girls' Frontline 2: Exilium* `.bundle` files
- 📦 Recursive processing and splitting of concatenated bundles into numbered parts
- ⚡ Optional multithreading for faster processing (system dependent)
- ✅ Verification mode to check headers and file sizes

## Usage

### Basic decryption

```
gf2_ab_decrypt <input_dir>
```
This reads all `.bundle` files from `<input_dir>` and writes results to `./AssetBundles_Decrypted`.

### Options

- `--out <output_dir>`
Set a custom output directory instead of the default `./AssetBundles_Decrypted`.
- `--parallel`
Enable multithreaded processing.
- `--verify`
After decryption, check that all output files have the correct header and valid size.
- `--verify-only`
Skip decryption and only run verification on the given directory.

### Example

```
# Decrypt all files in ./AssetBundles_Windows into ./out with multithreaded processing and verify them
gf2_ab_decrypt ./AssetBundles_Windows --out ./out --parallel --verify
```
```
# Just verify existing bundles
gf2_ab_decrypt ./AssetBundles_Decrypted --verify-only
```

## Build

Requires a C++17-capable compiler (e.g., GCC 9+, Clang 10+, MSVC 2019+).

### Using make

```
make
```

### Using g++

```
g++ -std=c++17 -O2 -pthread -Iinclude -o ./gf2_ab_decrypt ./src/main.cpp ./src/crypto.cpp ./src/file_io.cpp ./src/verify.cpp
```

### Anything else

This program only uses the standard library so anything should work without much trouble.

## Disclaimer

This program is provided for educational and research purposes only.
It does not grant any rights to redistribute or use decrypted assets.
The authors are not affiliated with the creators of *Girls' Frontline 2: Exilium*.
