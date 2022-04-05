#include <cstdint>
#include <fstream>
#include <optional>
#include <queue>
#include <cassert>
#include <fmt/format.h>
#include <vector>

std::optional <std::vector<uint8_t>> load_from_file(const std::string& path) {
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
	std::vector <uint8_t> rom(temp.begin(), temp.end());

	return { rom };
}

int main(int argc, char** argv) {
	if(argc < 2) {
		fmt::print("Expected arguments: script-filename");
		return 1;
	}

	auto bytes_or_error = load_from_file(argv[1]);
	if(!bytes_or_error.has_value()) {
		fmt::print("Failed opening file!\n");
		return 1;
	}

	auto bytes = *bytes_or_error;
	unsigned pointer = 0;

	auto get32 = [&bytes](unsigned from) -> uint32_t {
		assert(from < bytes.size() && from + sizeof(uint32_t) < bytes.size());
		return *reinterpret_cast<uint32_t*>(&bytes[from]);
	};
	auto get16 = [&bytes](unsigned from) -> uint16_t {
		assert(from < bytes.size() && from + sizeof(uint16_t) < bytes.size());
		return *reinterpret_cast<uint16_t*>(&bytes[from]);
	};
	auto get8 = [&bytes](unsigned from) -> uint8_t {
		assert(from < bytes.size());
		return bytes[from];
	};

	const uint32_t script_base_address = 0x020182ad;

	std::priority_queue <uint32_t, std::deque<uint32_t>, std::greater<uint32_t>> offsets_to_disasm {};
	offsets_to_disasm.push(0x0);

	std::vector<bool> visited_bytes {};
	visited_bytes.resize(bytes.size());

	auto increment = [&](unsigned count) {
		for(unsigned i = pointer; i < pointer + count; ++i) {
			if(i >= visited_bytes.size()) {
				continue;
			}
			visited_bytes[i] = true;
		}

		pointer += count;
	};

	auto analyze = [&](uint32_t address) {
		if(address < script_base_address || address > script_base_address + bytes.size()) {
			fmt::print("Skipping analysis of 0x{:08x} - out of bounds. Did you copy the whole script?\n", address);
			return;
		}

		offsets_to_disasm.push(address - script_base_address);
	};

	while(!offsets_to_disasm.empty()) {
		pointer = offsets_to_disasm.top();
		offsets_to_disasm.pop();

		if(visited_bytes[pointer]) {
			continue;
		}

		fmt::print("\n@Function 0x{:08x}\n\n", script_base_address + pointer);

		auto p = [&]() {
			return script_base_address + pointer;
		};

		bool finished = false;
		while((pointer < bytes.size()) && !finished) {
			auto byte = bytes[pointer];
			switch(byte) {
				case 0x0: {
					fmt::print("0x{:08x}  | nop\n", p());
					increment(1);
					break;
				}
				case 0x2: {
					fmt::print("0x{:08x}  | exit\n", p());
					increment(1);
					finished = true;
					break;
				}
				case 0x3: {
					fmt::print("0x{:08x}  | return\n", p());
					increment(1);
					finished = true;
					break;
				}
				case 0x4: {
					auto addr = *reinterpret_cast<uint32_t*>(&bytes[pointer + 1]);
					fmt::print("0x{:08x}  | call 0x{:08x}\n", p(), addr);
					analyze(addr);
					increment(5);
					break;
				}
				case 0x6: {
					fmt::print("0x{:08x}  | goto_if {}, 0x{:08x}\n", p(), get8(pointer + 1), get32(pointer + 2));
					analyze(get32(pointer + 2));
					increment(6);
					break;
				}
				case 0x9: {
					fmt::print("0x{:08x}  | callstd {}\n", p(), bytes[pointer + 1]);
					increment(2);
					break;
				}
				case 0x11: {
					fmt::print("0x{:08x}  | setptr {}, 0x{:08x}\n", p(), get8(pointer + 1), get32(pointer + 2));
					increment(6);
					break;
				}
				case 0x12: {
					fmt::print("0x{:08x}  | loadbytefromptr {}, 0x{:08x}\n", p(), get8(pointer + 1),
					           get32(pointer + 2));
					increment(6);
					break;
				}
				case 0x13: {
					fmt::print("0x{:08x}  | setptrbyte {}, 0x{:08x}\n", p(), get8(pointer + 1), get32(pointer + 2));
					increment(6);
					break;
				}
				case 0x16: {
					fmt::print("0x{:08x}  | setvar 0x{:04x}, 0x{:04x}\n", p(), get16(pointer + 1),
					           get16(pointer + 3));
					increment(5);
					break;
				}
				case 0x17: {
					fmt::print("0x{:08x}  | addvar 0x{:04x}, 0x{:04x}\n", p(), get16(pointer + 1),
					           get16(pointer + 3));
					increment(5);
					break;
				}
				case 0x18: {
					fmt::print("0x{:08x}  | subvar 0x{:04x}, 0x{:04x}\n", p(), get16(pointer + 1),
					           get16(pointer + 3));
					increment(5);
					break;
				}
				case 0x19: {
					fmt::print("0x{:08x}  | copyvar 0x{:04x}, 0x{:04x}\n", p(), get16(pointer + 1),
					           get16(pointer + 3));
					increment(5);
					break;
				}
				case 0x0f: {
					auto dest = bytes[pointer + 1];
					auto value = *reinterpret_cast<uint32_t*>(&bytes[pointer + 2]);
					fmt::print("0x{:08x}  | loadword {:04x}, 0x{:08x}\n", p(), dest, value);
					increment(6);
					break;
				}
				case 0x21: {
					auto var = get16(pointer + 1);
					auto val = get16(pointer + 3);
					//  FIXME: what is var?
					fmt::print("0x{:08x}  | compvar {:04x}, {}\n", p(), var, val);
					increment(5);
					break;
				}
				case 0x23: {
					auto addr = *reinterpret_cast<uint32_t*>(&bytes[pointer + 1]);
					fmt::print("0x{:08x}  | callnative 0x{:08x}\n", p(), addr);
					increment(5);
					break;
				}
				case 0x27: {
					fmt::print("0x{:08x}  | waitstate\n", p());
					increment(1);
					break;
				}
				case 0x2f: {
					fmt::print("0x{:08x}  | playse {}\n", p(), get16(pointer + 1));
					increment(3);
					break;
				}
				case 0x5a: {
					fmt::print("0x{:08x}  | faceplayer\n", p());
					increment(1);
					break;
				}
				case 0x6a: {
					fmt::print("0x{:08x}  | freezeobjects\n", p());
					increment(1);
					break;
				}
				case 0x6c: {
					fmt::print("0x{:08x}  | release\n", p());
					increment(1);
					break;
				}
				default: {
					fmt::print("Unimplemented opcode! {:02x}\n", byte);
					assert(false);
				}
			}
		}
	}
}