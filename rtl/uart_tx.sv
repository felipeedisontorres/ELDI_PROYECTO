module uart_tx #(
    parameter int CLKS_PER_BIT = 868
) (
    input  logic       clk,
    input  logic       reset,
    input  logic       start,
    input  logic [7:0] data,
    output logic       tx,
    output logic       busy
);
    localparam int BW   = $clog2(CLKS_PER_BIT);
    localparam int LAST = CLKS_PER_BIT - 1;

    logic [9:0]    sr_tx;
    logic [3:0]    bit_tx;
    logic [BW-1:0] baud_tx;
    logic          tick;

    assign busy = (bit_tx != 4'd0);
    assign tick = (baud_tx == LAST[BW-1:0]);
    assign tx   = sr_tx[0];

    always_ff @(posedge clk) begin
        if (reset | ~busy | tick) baud_tx <= '0;
        else                      baud_tx <= baud_tx + 1'b1;
    end

    always_ff @(posedge clk) begin
        if (reset) begin
            sr_tx  <= '1;
            bit_tx <= 4'd0;
        end else if (start) begin
            sr_tx  <= {1'b1, data, 1'b0};
            bit_tx <= 4'd10;
        end else if (tick) begin
            sr_tx  <= {1'b1, sr_tx[9:1]};
            bit_tx <= bit_tx - 4'd1;
        end
    end
endmodule
