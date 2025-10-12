/*
 * Copyright (c) 2025 ReJ aka Renaldas Zioma
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_rejunity_ym2413_ika_opll (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
  assign uo_out       = o_ikaopll_main[15: 8];
  assign uio_out[7:2] = o_ikaopll_main[7 : 2];
  assign uio_oe       = 8'b1111_1100;

  ///////////////////////////////////////////////////////////
  //////  Clocking information
  ////

  /*
      phiM(XIN)   ¯|_|¯|_|¯|_|¯|_|¯|_|¯|_|¯|_|¯|_|¯|_|¯|_|¯|_|
      prescaler   -3-|-0-|-1-|-2-|-3-|-0-|-1-|-2-|-3-|-0-|-1-|
      phi1p       ¯|_________|¯¯¯¯¯|_________|¯¯¯¯¯|_________|
      phi1n       ___|¯¯¯¯¯|_________|¯¯¯¯¯|_________|¯¯¯¯¯|__

      phi1pcen    _______|¯¯¯|___________|¯¯¯|___________|¯¯¯|
      phi1ncen    ¯¯¯|___________|¯¯¯|___________|¯¯¯|________
      dacen       ___|¯¯¯|___________|¯¯¯|___________|¯¯¯|____
  */

  // BUS IO wires
  wire            IC_n =  rst_n; // chip reset
  wire [7:0]      DIN  =  ui_in;
  wire            CS_n =  1'b1;
  wire            WR_n = ~uio_in[1];
  wire            A0   =  uio_in[0];

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, 1'b0};


// main chip
  wire                o_XOUT;
  wire        [1:0]   o_D;
  wire                o_D_OE;
  wire                o_DAC_EN_MO;
  wire                o_DAC_EN_RO;
  wire                o_IMP_NOFLUC_SIGN;
  wire        [7:0]   o_IMP_NOFLUC_MAG;
  wire signed [9:0]   o_IMP_FLUC_SIGNED_MO;
  wire signed [9:0]   o_IMP_FLUC_SIGNED_RO;
  wire                o_ACC_SIGNED_STRB;
  wire signed [15:0]  o_ikaopll_main;
IKAOPLL #(
    .FULLY_SYNCHRONOUS          (1                          ),
    .FAST_RESET                 (1                          ),
    .ALTPATCH_CONFIG_MODE       (0                          ), // VRC7 patch enable
    .USE_PIPELINED_MULTIPLIER   (1                          )
) main (
    .i_XIN_EMUCLK               (clk                        ),
    .o_XOUT                                                  ,

    .i_phiM_PCEN_n              (1'b0                       ),

    .i_IC_n                     (IC_n                       ),

    .i_ALTPATCH_EN              (1'b0                       ),

    .i_CS_n                     (CS_n                       ),
    .i_WR_n                     (WR_n                       ),
    .i_A0                       (A0                         ),

    .i_D                        (DIN                        ),
    .o_D                                                     ,
    .o_D_OE                                                  ,

    .o_DAC_EN_MO                                             ,
    .o_DAC_EN_RO                                             ,
    .o_IMP_NOFLUC_SIGN                                       ,
    .o_IMP_NOFLUC_MAG                                        ,
    .o_IMP_FLUC_SIGNED_MO                                    ,
    .o_IMP_FLUC_SIGNED_RO                                    ,
    .o_ACC_SIGNED_STRB                                       ,
    .o_ACC_SIGNED               (o_ikaopll_main             )
);

endmodule
