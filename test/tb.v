`default_nettype none
`timescale 1ns / 1ps

/* This testbench just instantiates the module and makes some convenient wires
   that can be driven / tested by the cocotb test.py.
*/
module tb ();

  // Dump the signals to a VCD file. You can view it with gtkwave or surfer.
  initial begin
    $dumpfile("tb.vcd");
`ifdef GL_TEST
    $dumpvars(1, tb);
`else
    $dumpvars(0, tb);
`endif
    #1;
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;
`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  tt_um_rejunity_ym2413_ika_opll user_project (

      // Include power ports for the Gate Level test:
`ifdef GL_TEST
      .VPWR(VPWR),
      .VGND(VGND),
`endif

      .ui_in  (ui_in),    // Dedicated inputs
      .uo_out (uo_out),   // Dedicated outputs
      .uio_in (uio_in),   // IOs: Input path
      .uio_out(uio_out),  // IOs: Output path
      .uio_oe (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
      .ena    (ena),      // enable - goes high when design is selected
      .clk    (clk),      // clock
      .rst_n  (rst_n)     // not reset
  );

  wire            IC   =  ~rst_n;
  wire [7:0]      DIN  =  ui_in;
  wire            A0   =  uio_in[0];
  wire            CS   =  uio_in[1];
  wire            WR   =  uio_in[2];

  // wire            melody = uio_out[3];
  // wire            rhytm  = uio_out[4];
  // wire [16:0]     master_out = 16'sd32767 + $signed({uo_out, uio_out[7:5]});

  reg [16:0]      master_out;
  reg [16:0]      master_acc;
  reg [6:0]       master_counter;
  wire            master_strobe = (master_counter == 71);
  always @(posedge clk) begin
      if (~rst_n) begin
          master_out <= 72*128;
          master_acc <= 0;
          master_counter <= 0;
      end else if (master_strobe) begin
          master_out <= master_acc;
          master_acc <= 0;
          master_counter <= 0;
      end else begin
        master_acc <= master_acc + uo_out;
        // master_acc <= master_acc + {9'b0, (uo_out[7] ? ~uo_out[6:0] : uo_out[6:0])};
        master_counter <= master_counter + 1;
      end
  end

  reg [18:0]      pwm_acc;
  always @(posedge clk) begin
      if (~rst_n) begin
          pwm_acc <= 16'h2A2A * 4;
      end else begin
          // pwm_acc <= { uio_out[7], pwm_acc[17:1] };
          // pwm_acc <= (uio_out[7] << 8) + (pwm_acc * 15) / 16;
          pwm_acc <= (uio_out[7] << 10) + (pwm_acc * 253) / 256;      // 0.98828 approx a=0.98748
          // pwm_acc <= (uio_out[7] << 10) + (pwm_acc * 4042) / 4096; 
      end
  end

  reg [18:0]      pwm2_acc;
  always @(posedge clk) begin
      if (~rst_n) begin
          pwm2_acc <= 16'h2A2A * 4;
      end else begin
          pwm2_acc <= (uio_out[6] << 10) + (pwm2_acc * 253) / 256;      // 0.98828 approx a=0.98748
      end
  end

endmodule
