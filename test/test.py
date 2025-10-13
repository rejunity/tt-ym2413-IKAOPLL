# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

async def set_register(dut, reg, value, wait = 0, wait_between_writes = 0):
    async def write(dut, a0, value):
        # [WR, CS, A0]
        dut.uio_in.value = 0b110 | a0   # @(posedge i_CLK) o_A0 = i_TARGET_ADDR;
        await ClockCycles(dut.clk, 1)
        dut.uio_in.value = 0b100 | a0   # @(negedge i_CLK) o_CS_n = 1'b0;
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = reg           # @(posedge i_CLK) o_DATA = i_WRITE_DATA;
        await ClockCycles(dut.clk, 1)
        dut.uio_in.value = 0b000 | a0   # @(negedge i_CLK) o_WR_n = 1'b0;
        await ClockCycles(dut.clk, 1)
        dut.uio_in.value = 0b110 | a0   # @(negedge i_CLK) o_WR_n = 1'b1; o_CS_n = 1'b1;
        await ClockCycles(dut.clk, 1)
        # TODO: set data bus to high impedance @(posedge i_CLK) o_DATA = 8'hZZ;

    print(f"WRITE [{hex(reg)}] <= {value}")
    await write(dut, 0, reg)
    if wait_between_writes > 0: await ClockCycles(dut.clk, wait_between_writes)
    await write(dut, 1, value)
    if wait > 0:                await ClockCycles(dut.clk, wait)

@cocotb.test()
async def test_reset(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    # clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut.uio_in.value = 0b110 # /WR=1, /CS=1, A0=0

    dut._log.info("Settle")
    await ClockCycles(dut.clk, 1000) # settle

    for n in range(10):
        dut.uio_in.value = 0b111
        await ClockCycles(dut.clk, 1)
        print(dut.uo_out, dut.uio_out)

    for n in range(10):
        dut.uio_in.value = 0b100
        await ClockCycles(dut.clk, 1)
        print(dut.uo_out, dut.uio_out)

    for n in range(10):
        dut.uio_in.value = 0b000
        await ClockCycles(dut.clk, 1)
        print(dut.uo_out, dut.uio_out)

@cocotb.test()
async def test_ym(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    # clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut.uio_in.value = 0b110 # /WR=1, /CS=1, A0=0

    dut._log.info("Settle")
    await ClockCycles(dut.clk, 1500) # settle

    dut._log.info("YM reg write: custom instrument")
    await set_register(dut, 0x00, 0x00, wait=100, wait_between_writes=100)
    await set_register(dut, 0x00, 0x00, wait=100, wait_between_writes=100)
    await set_register(dut, 0x01, 0x00, wait=100, wait_between_writes=100)
    await set_register(dut, 0x02, 0x00, wait=100, wait_between_writes=100)
    await set_register(dut, 0x03, 0x18, wait=100, wait_between_writes=100)
    await set_register(dut, 0x04, 0x7A, wait=100, wait_between_writes=100)
    await set_register(dut, 0x05, 0x59, wait=100, wait_between_writes=100)
    await set_register(dut, 0x06, 0x30, wait=100, wait_between_writes=100)
    await set_register(dut, 0x07, 0x59, wait=100, wait_between_writes=100)

    # rhythm
    dut._log.info("YM reg write: rhytm")
    await set_register(dut, 0x16, 0x20, wait=800, wait_between_writes=150)
    await set_register(dut, 0x17, 0x50, wait=800, wait_between_writes=150)
    await set_register(dut, 0x18, 0xC0, wait=800, wait_between_writes=150)
    await set_register(dut, 0x26, 0x05, wait=800, wait_between_writes=150)
    await set_register(dut, 0x27, 0x05, wait=800, wait_between_writes=150)
    await set_register(dut, 0x28, 0x01, wait=800, wait_between_writes=150)
    await set_register(dut, 0x0E, 0x30, wait=100, wait_between_writes=100)
    
    # inst test
    dut._log.info("YM reg write: instrument test")
    await set_register(dut, 0x10, 0xAC, wait=800, wait_between_writes=150)
    await set_register(dut, 0x30, 0xE0, wait=800, wait_between_writes=150)
    await set_register(dut, 0x20, 0x17, wait=800, wait_between_writes=150)
    dut._log.info("YM playing")
    # await ClockCycles(dut.clk, 320000) # long wait
    await ClockCycles(dut.clk, 32000)
    dut._log.info("YM reg write: instrument close")
    await set_register(dut, 0x20, 0x07, wait=800, wait_between_writes=150)
