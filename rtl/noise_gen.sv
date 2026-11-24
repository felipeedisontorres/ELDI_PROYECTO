module noise_gen (
    input  logic       clk,
    input  logic       reset,
    input  logic [1:0] ch,
    input  logic       wr_in,
    input  logic [1:0] level,
    input  logic [7:0] din,
    output logic [7:0] noisy
);
    logic [15:0] lfsr;
    logic        fb, lfsr_en, hit;
    logic [7:0]  thr;

    assign lfsr_en = ~(ch[1] | ch[0] | wr_in);
    assign fb      = lfsr[0] ^ lfsr[2] ^ lfsr[3] ^ lfsr[5];

    always_ff @(posedge clk) begin
        if (reset)        lfsr <= 16'hACE1;
        else if (lfsr_en) lfsr <= {fb, lfsr[15:1]};
    end

    assign thr   = {2'b00, level, 4'b0000};
    assign hit   = (lfsr[7:0] < thr);
    assign noisy = hit ? {8{lfsr[8]}} : din;
endmodule
