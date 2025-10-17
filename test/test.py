# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

NTSC_FREQ = 3_579_545

async def set_register(dut, reg, value, wait = 800, wait_between_writes = 150):
    async def write(dut, a0, value):
        # MSB [..., WR, CS, A0] LSB
        dut.uio_in.value = 0b000 | a0   # @(posedge i_CLK) o_A0 = i_TARGET_ADDR;
        await ClockCycles(dut.clk, 1)
        dut.uio_in.value = 0b010 | a0   # @(negedge i_CLK) o_CS_n = 1'b0;
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = value         # @(posedge i_CLK) o_DATA = i_WRITE_DATA;
        await ClockCycles(dut.clk, 1)
        dut.uio_in.value = 0b110 | a0   # @(negedge i_CLK) o_WR_n = 1'b0;
        await ClockCycles(dut.clk, 1)
        dut.uio_in.value = 0b000 | a0   # @(negedge i_CLK) o_WR_n = 1'b1; o_CS_n = 1'b1;
        await ClockCycles(dut.clk, 1)
        # TODO: set data bus to high impedance @(posedge i_CLK) o_DATA = 8'hZZ;

    print(f"WRITE [{hex(reg)}] <= {value}")
    await write(dut, 0, reg)
    if wait_between_writes > 0: await ClockCycles(dut.clk, wait_between_writes)
    await write(dut, 1, value)
    if wait > 0:                await ClockCycles(dut.clk, wait)


async def reset(dut):
    dut._log.info("Start")

    # Set the clock period to 280 ns 3.579 MHz - NTSC frequency
    # NTSC is default expected clock for YM2413
    # clock = Clock(dut.clk, 1_000_000_000 // NTSC_FREQ, unit ="ns")
    clock = Clock(dut.clk, 1_000_000_000 // NTSC_FREQ, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 100) # has to be at least 72 cycles long to reset internal d9reg
    dut.rst_n.value = 1
    dut.uio_in.value = 0b000 # WR=0, CS=0, A0=0

    return clock

async def play(dut, ms = 10):
    dut._log.info(f"YM playing for {ms}ms...")
    cycles_per_step = 1000
    for n in range(NTSC_FREQ * ms // (1000 * cycles_per_step)):
        await ClockCycles(dut.clk, cycles_per_step)
        print(dut.uo_out.value)

@cocotb.test()
async def test_reset(dut):
    await reset(dut)

    dut._log.info("Settle")
    await ClockCycles(dut.clk, 1000) # settle

@cocotb.test()
async def test_ym_sine(dut):
    await reset(dut)

    dut._log.info("Settle")
    await ClockCycles(dut.clk, 100)

    dut._log.info("YM reg write: custom sine instrument from https://www.smspower.org/Development/YM2413ReverseEngineeringNotes2015-02-09")
    # see https://www.smspower.org/Development/YM2413ReverseEngineeringNotes2015-02-09 "Sampling the YM2413 output"    # Very simple test program: writes the following YM2413 registers
    # R#0x00 = 0x20
    # R#0x01 = 0x20
    # R#0x02 = 0x3F
    # R#0x03 = 0x00
    # R#0x04 = 0xFF
    # R#0x05 = 0xFF
    # R#0x06 = 0x0F
    # R#0x07 = 0x0F
    # R#0x10 = 0x61
    # R#0x30 = 0x00
    # R#0x20 = 0x12    
    await set_register(dut, 0x00, 0x20)
    await set_register(dut, 0x01, 0x20)
    await set_register(dut, 0x02, 0x3F)
    await set_register(dut, 0x03, 0x00)
    await set_register(dut, 0x04, 0xFF)
    await set_register(dut, 0x05, 0xFF)
    await set_register(dut, 0x06, 0x0F)
    await set_register(dut, 0x07, 0x0F)
    await set_register(dut, 0x10, 0xAC) # 0x61)
    await set_register(dut, 0x30, 0x00) # volume=0 (the maximum volume setting) actually it is attenuation!
    await set_register(dut, 0x20, 0x1C) # 0x12)
    # This sets up a custom instrument that plays a sine wave (regs 0-7) and then plays this instrument on channel 0 with maximum volume. 

    await play(dut)

    dut._log.info("Done")


@cocotb.test()
async def test_ym_custom_instrument(dut):
    await reset(dut)

    dut._log.info("Settle")
    await ClockCycles(dut.clk, 1500) # settle

    dut._log.info("YM reg write: custom instrument")
    await set_register(dut, 0x00, 0x00, wait=100, wait_between_writes=100)
    await set_register(dut, 0x01, 0x00, wait=100, wait_between_writes=100)
    await set_register(dut, 0x02, 0x00, wait=100, wait_between_writes=100)
    await set_register(dut, 0x03, 0x18, wait=100, wait_between_writes=100)
    await set_register(dut, 0x04, 0x7A, wait=100, wait_between_writes=100)
    await set_register(dut, 0x05, 0x59, wait=100, wait_between_writes=100)
    await set_register(dut, 0x06, 0x30, wait=100, wait_between_writes=100)
    await set_register(dut, 0x07, 0x59, wait=100, wait_between_writes=100)
    
    # inst test
    dut._log.info("YM reg write: instrument test")
    await set_register(dut, 0x10, 0xAC, wait=800, wait_between_writes=150)
    await set_register(dut, 0x20, 0x17, wait=800, wait_between_writes=150) # key on
    await set_register(dut, 0x30, 0xE0, wait=800, wait_between_writes=150)
    dut._log.info("YM playing")
    
    await play(dut)

    dut._log.info("YM reg write: instrument key off")
    await set_register(dut, 0x20, 0x07, wait=800, wait_between_writes=150) # key off

@cocotb.test()
async def test_ym_rhytm(dut):
    await reset(dut)

    dut._log.info("Settle")
    await ClockCycles(dut.clk, 1500) # settle

    # rhythm
    dut._log.info("YM reg write: rhytm")
    await set_register(dut, 0x16, 0x20, wait=800, wait_between_writes=150)
    await set_register(dut, 0x17, 0x50, wait=800, wait_between_writes=150)
    await set_register(dut, 0x18, 0xC0, wait=800, wait_between_writes=150)
    await set_register(dut, 0x26, 0x05, wait=800, wait_between_writes=150)
    await set_register(dut, 0x27, 0x05, wait=800, wait_between_writes=150)
    await set_register(dut, 0x28, 0x01, wait=800, wait_between_writes=150)
    await set_register(dut, 0x0E, 0x30, wait=100, wait_between_writes=100)
    
    await play(dut)

# @cocotb.test()
async def test_ym_instruments(dut):
    await reset(dut)

    dut._log.info("Settle")
    await ClockCycles(dut.clk, 1500) # settle

    dut._log.info("YM reg write: reset")
    for n in range(0x0F):
        await set_register(dut, n, 0x00, wait=100, wait_between_writes=100)
    
    dut._log.info("YM reg write: instruments")
    # fnum@[7:0]
    await set_register(dut, 0x10, 0xAC)
    await set_register(dut, 0x11, 0xAC)
    await set_register(dut, 0x12, 0xAC)
    await set_register(dut, 0x13, 0xAC)
    await set_register(dut, 0x14, 0xAC)
    await set_register(dut, 0x15, 0xAC)
    await set_register(dut, 0x16, 0xAC)
    await set_register(dut, 0x17, 0xAC)
    await set_register(dut, 0x18, 0xAC)

    # key@[4], block@[3:1], fnum_msb@[0] 
    await set_register(dut, 0x20, 0x00|(0<<1))
    await set_register(dut, 0x21, 0x00|(1<<1))
    await set_register(dut, 0x22, 0x00|(2<<1))
    await set_register(dut, 0x23, 0x00|(3<<1))
    await set_register(dut, 0x24, 0x00|(4<<1))
    await set_register(dut, 0x25, 0x00|(5<<1))
    await set_register(dut, 0x26, 0x00|(6<<1))
    await set_register(dut, 0x27, 0x00|(7<<1))
    await set_register(dut, 0x28, 0x00|(4<<1))

    await set_register(dut, 0x21, 0x12|(7<<1))
    await set_register(dut, 0x22, 0x12|(7<<1))
    await set_register(dut, 0x23, 0x12|(7<<1))

    # intrument@[7:4], volume@[3:0]
    await set_register(dut, 0x30, 0x0F)
    await set_register(dut, 0x31, 0x1C)
    await set_register(dut, 0x32, 0x2C)
    await set_register(dut, 0x33, 0x3C)
    await set_register(dut, 0x34, 0x4C)
    await set_register(dut, 0x35, 0x5C)
    await set_register(dut, 0x36, 0x10)
    await set_register(dut, 0x37, 0x10)
    await set_register(dut, 0x38, 0x10)

    await play(dut)

    dut._log.info("YM reg write: instrument key off")
    await set_register(dut, 0x20, 0x18)
    await set_register(dut, 0x21, 0x18)


  #  #1700000;
  #   `DD IKAOPLL_write(1'b0, 8'h21, phiMref, CS_n, WR_n, A0, DIN);
  #   `AD IKAOPLL_write(1'b1, 8'h02, phiMref, CS_n, WR_n, A0, DIN);

  #   #1000000;
  #   `DD IKAOPLL_write(1'b0, 8'h21, phiMref, CS_n, WR_n, A0, DIN);
  #   `AD IKAOPLL_write(1'b1, 8'h32, phiMref, CS_n, WR_n, A0, DIN);

  #   #1700000;
  #   `DD IKAOPLL_write(1'b0, 8'h0E, phiMref, CS_n, WR_n, A0, DIN);
  #   `AD IKAOPLL_write(1'b1, 8'h3F, phiMref, CS_n, WR_n, A0, DIN);
  #   `DD IKAOPLL_write(1'b0, 8'h21, phiMref, CS_n, WR_n, A0, DIN);
  #   `AD IKAOPLL_write(1'b1, 8'h22, phiMref, CS_n, WR_n, A0, DIN);

  #   #2000000;
  #   `DD IKAOPLL_write(1'b0, 8'h0E, phiMref, CS_n, WR_n, A0, DIN);
  #   `AD IKAOPLL_write(1'b1, 8'h20, phiMref, CS_n, WR_n, A0, DIN);
  #   #100 IKAOPLL_write(1'b0, 8'h00, phiMref, CS_n, WR_n, A0, DIN);
  #   #100 IKAOPLL_write(1'b1, 8'h20, phiMref, CS_n, WR_n, A0, DIN);
  #   #100 IKAOPLL_write(1'b0, 8'h01, phiMref, CS_n, WR_n, A0, DIN);
  #   #100 IKAOPLL_write(1'b1, 8'h20, phiMref, CS_n, WR_n, A0, DIN);

  #   #1000000;
  #   `DD IKAOPLL_write(1'b0, 8'h21, phiMref, CS_n, WR_n, A0, DIN);
  #   `AD IKAOPLL_write(1'b1, 8'h12, phiMref, CS_n, WR_n, A0, DIN);

  #   #1700000;
  #   `DD IKAOPLL_write(1'b0, 8'h21, phiMref, CS_n, WR_n, A0, DIN);
  #   `AD IKAOPLL_write(1'b1, 8'h02, phiMref, CS_n, WR_n, A0, DIN);
  # 