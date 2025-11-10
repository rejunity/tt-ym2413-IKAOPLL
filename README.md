![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# ASIC replica of the classic YM2413 FM Synthesis audio chip in Tiny Tapeout
<p align="center" width="100%">
  <img width="25%" src="https://github.com/user-attachments/assets/4bce097f-8dfe-4803-ac3b-226b1049fe7a">
</p>

[YM2413 Verilog core](https://github.com/ika-musume/IKAOPLL) is written by Sehyeon Kim (Raki). It was reverse-engineered with only Yamaha's datasheet and die shots from Madov and Travis Goodspeed.

Originally developed as FPGA core, the code is well suitaed for ASIC and with just few minimal modifications it will be taped out on a 130 nm process using [Tiny Tapeout](https://tinytapeout.com) service.

## What is YM2413
The **YM2413**, a.k.a. **OPLL**, is FM synthesis sound chip manufactured by Yamaha Corporation in. It is related to Yamaha's OPL family of FM synthesis chips, and is a cost-reduced version of the YM3812 (OPL2).

<p align="center" width="100%">
  <img width="400" height="475" alt="image" src="https://github.com/user-attachments/assets/bf7c7b89-0ca9-43de-a536-a3dac51cc1dc" />
</p>

The YM2413 uses FM synthesis based on the OPL (FM Operator Type-L) series, which is a low-cost version of other forms of FM synthesis used in other chips with 4 or more FM operators. It can generate up to 9 voices with 2 FM operators for each channel. The last three channels can be swapped out for rhythm channels, which can use any of the 5 percussion sounds using the three channels.
To make the chip cheaper to manufacture, many of the internal registers were removed. The result of this is that the YM2413 can only play one user-defined instrument at a time; the other 15 instrument settings are hard-coded and cannot be altered by the user. There were other cost-cutting modifications: the number of waveforms was reduced to two, and an adder is not used to mix the channels; instead, the chip's built-in DAC plays each channel one after the other, and the output of this is usually passed through an analog filter. This is similar to what would be done on the YM2612 later on.


- [Read the documentation for project](docs/info.md)

## Technical specifications
- Clock rate: 3.579545 MHz
- Sound output: Mono
- Sound channels: 9
- Channels:
  * 9 FM channels
  * 6 FM channels + 3 rhythm channels
- Instruments: 15 pre-defined instruments and one user-defined sound
- FM channels: 6-9 channels (6 channels with rhythm mode, 9 channels without rhythm mode)
- Rhythm channels: 3 channels can be used for percussion sounds
- Percussion: 5 percussion sounds (bass drum, snare drum, tom-tom, top cymbal, hi-hat)

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that aims to make it easier and cheaper than ever to get your digital and analog designs manufactured on a real chip.

To learn more and get started, visit https://tinytapeout.com.

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://tinytapeout.com/discord)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

