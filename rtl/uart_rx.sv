module uart_rx #(
    parameter int CLKS_PER_BIT = 868
) (
    input  logic       clk,
    input  logic       reset,
    input  logic       rx,
    output logic       rx_valid,
    output logic [7:0] rx_data
);
    localparam int BW   = $clog2(CLKS_PER_BIT);
    localparam int HALF = CLKS_PER_BIT/2 - 1;
    localparam int LAST = CLKS_PER_BIT - 1;

    logic          rx_busy;
    logic [BW-1:0] baud_rx;
    logic [3:0]    bit_rx;
    logic          sample;

    assign sample   = (baud_rx == HALF[BW-1:0]);
    assign rx_valid = sample & (bit_rx == 4'd9);

    always_ff @(posedge clk) begin
        if (reset)        rx_busy <= 1'b0;
        else if (rx_busy) rx_busy <= ~rx_valid;
        else              rx_busy <= ~rx;
    end

    always_ff @(posedge clk) begin
        if (reset | ~rx_busy | (baud_rx == LAST[BW-1:0])) baud_rx <= '0;
        else                                              baud_rx <= baud_rx + 1'b1;
    end

    always_ff @(posedge clk) begin
        if (reset | ~rx_busy) bit_rx <= '0;
        else if (sample)      bit_rx <= bit_rx + 1'b1;
    end

    always_ff @(posedge clk) begin
        if (reset)       rx_data <= '0;
        else if (sample) rx_data <= {rx, rx_data[7:1]};
    end
endmodule
