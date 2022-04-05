#include <cstdint>
#include <numeric>
#include <cstdio>

int main() {
	//  0x0000b100
	const uint8_t special_byte { 0xb1 };
	const uint32_t words[] = { 0x0000001 + (static_cast<uint16_t>(special_byte) << 8), 0x00001337 };

	uint32_t magic = 0xF0DBEB15;
	for(auto& word : words) {
		magic = std::rotr(magic, 5);
		magic = magic ^ word;
		magic = (magic + 2 * word);
		std::printf("Round magic: %02x\n", magic);
	}

	std::printf("Final magic: %02x\n", magic);

	const uint32_t w0 = (words[0] & 0xFFFFu) + (magic << 16u);
	std::printf("W0: %02x\n", w0);
	std::printf("W1: %02x\n", words[1]);
}
