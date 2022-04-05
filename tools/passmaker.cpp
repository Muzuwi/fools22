#include <cstdint>
#include <cstdio>

using u8 = uint8_t;
using u16 = uint16_t;
using u32 = uint32_t;

int main() {
//	const u8 regs[16] = { 0xbb, 0xbb, 0xbb, 0xbb,
//	                      0xbb, 0xbb, 0xff, 0xff,
//	                      0xff, 0xff, 0xff, 0xff,
//	                      0xff, 0xff, 0xff, 0xff };
//	const u8 regs[16] = { 186, 105, 237, 141, 180, 164, 203, 71, 12, 93, 255, 255, 255, 255, 255, 255 };
	const u8 regs[16] = { 215, 210, 199, 234, 200, 222, 220, 234, 224, 192, 192, 192, 192, 192, 192, 192 };

	//  output is: x8001=c888, x8003=705c

	const u16 multipliers[20] = {
			0x0049, 0x0061, 0x000d, 0x0029,
			0x0043, 0x0065, 0x0059, 0x008b,
			0x0047, 0x0053, 0x003b, 0x00b5,
			0x007f, 0x00a3, 0x0067, 0x00a3,
			0x0095, 0x00c1, 0x00d3, 0x0097
	};

	const u16 offsets[20] = {
			0x18df, 0x13eb, 0x11ef, 0x1145,
			0x12df, 0x0dfd, 0x13af, 0x149f,
			0x0fef, 0x0fb5, 0x0e75, 0x11fb,
			0x1237, 0x125f, 0x107b, 0x1951,
			0x1b47, 0x151f, 0x14b1, 0x13eb
	};

//	u16 current_iv = 0x1b39 + regs[0];
//	for(unsigned i = 0; i < 20; ++i) {
//		const auto reg_offset = ((i != 19) ? regs[((i + 1) % 10)] : 0);
//		const u16 v = (multipliers[i] * current_iv + offsets[i]);
//		if(i == 9) {
//			std::printf("x8003: %04x\n", v);
//			current_iv = 0x0539 + regs[0];
//		} else {
//			std::printf("Current round V=%04x\n", v + reg_offset);
//			current_iv = v + reg_offset;
//		}
//	}

	u16 current_iv = 0x1b39 + regs[0];
	for(unsigned i = 0; i < 10; ++i) {
		const auto reg_offset = ((i != 9) ? regs[((i + 1) % 10)] : 0);
		const u16 v = (multipliers[i] * current_iv + offsets[i]);
		current_iv = v + reg_offset;
		if(i != 9) {
			std::printf("Current round V=%04x\n", current_iv);
		}
	}
	std::printf("x8003: %04x\n", current_iv);

	current_iv = 0x0539 + regs[0];
	for(unsigned i = 0; i < 10; ++i) {
		const auto reg_offset = ((i != 9) ? regs[((i + 1) % 10)] : 0);
		const u16 v = (multipliers[10 + i] * current_iv + offsets[10 + i]);
		current_iv = v + reg_offset;
		if(i != 9) {
			std::printf("Current round V=%04x\n", v);
		}
	}
	std::printf("x8001: %04x\n", current_iv);
}