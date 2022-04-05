#include <cstdint>
#include <fstream>
#include <optional>
#include <fmt/format.h>
#include <vector>

std::optional<std::vector<uint8_t>> load_from_file(const std::string& path) {
	std::ifstream file;
	std::vector<char> temp;
	file.open(path, std::ios::binary);
	if(!file.good()) {
		return {};
	}

	file.seekg(0, file.end);
	size_t fileSize = file.tellg();
	file.seekg(0, file.beg);
	temp.resize(fileSize);
	file.read(&temp[0], fileSize);
	file.close();
	std::vector<uint8_t> rom(temp.begin(), temp.end());

	return { rom };
}

int main(int argc, char** argv) {
	if(argc != 3) {
		fmt::print("Expected arguments: fname1 fname2\n");
		return 1;
	}
	
	auto f1name = std::string{argv[1]};
	auto f2name = std::string{argv[2]};
	
	auto f1_or_error = load_from_file(f1name);
	auto f2_or_error = load_from_file(f2name);
	if(!f1_or_error.has_value() || !f2_or_error.has_value()) {
		fmt::print("Could not open files\n");
		return 1;
	}

	auto f1 = *f1_or_error;
	auto f2 = *f2_or_error;
	
	if(f1.size() != f2.size()) {
		fmt::print("Files are not the same size\n");
		return 2;
	}
	
	auto print_bytes = [&](size_t start, size_t len) {
		fmt::print("file {:<16}: ", f1name);
		for(size_t i = start; i < start + len; ++i) {
			fmt::print("{:02x} ", f1[i]);
		} fmt::print("\n");
		
		fmt::print("file {:<16}: ", f2name);
		for(size_t i = start; i < start + len; ++i) {
			fmt::print("{:02x} ", f2[i]);
		} fmt::print("\n");
	};
	
	std::optional<size_t> diff_region {};
	for(size_t i = 0; i < f1.size(); i++) {
		if(f1[i] == f2[i]) {
			if(diff_region.has_value()) {
				fmt::print("From bytes {} to {}:\n", *diff_region, i - 1);
				print_bytes(*diff_region, i - *diff_region);
				diff_region = {std::nullopt};
			}
			continue;
		}
		
		if(!diff_region.has_value()) {
			diff_region = {i};
		}
	}
}

