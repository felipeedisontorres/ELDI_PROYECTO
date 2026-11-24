module bram_sdp #(
    parameter int AW = 16,
    parameter int DW = 8
) (
    input  logic          clk,
    input  logic          we,
    input  logic [AW-1:0] waddr,
    input  logic [DW-1:0] din,
    input  logic [AW-1:0] raddr,
    output logic [DW-1:0] dout
);
    logic [DW-1:0] mem [0:(1<<AW)-1];

`ifndef SYNTHESIS
    initial begin
        for (int i = 0; i < (1<<AW); i++) mem[i] = '0;
    end
`endif

    always_ff @(posedge clk) begin
        if (we) mem[waddr] <= din;
        dout <= mem[raddr];
    end
endmodule
