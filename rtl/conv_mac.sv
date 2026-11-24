module conv_mac (
    input  logic               clk,
    input  logic               reset,
    input  logic [1:0]         ksel,
    input  logic [3:0]         tap,
    input  logic [7:0]         pix,
    output logic signed [14:0] acc
);
    logic signed [7:0]  w, w_q;
    logic        [7:0]  pix_q;
    logic signed [16:0] prod_full;
    logic signed [14:0] prod, sum;
    logic               acc_clr;

    always_comb begin
        w = 8'sd0;
        case (ksel)
            2'b00: case (tap)
                       4'd1, 4'd3, 4'd7, 4'd9: w = 8'sd1;
                       4'd2, 4'd4, 4'd6, 4'd8: w = 8'sd2;
                       4'd5:                   w = 8'sd4;
                       default:                w = 8'sd0;
                   endcase
            2'b01: case (tap)
                       4'd2, 4'd4, 4'd6, 4'd8: w = 8'sd16;
                       4'd5:                   w = -8'sd64;
                       default:                w = 8'sd0;
                   endcase
            2'b10: case (tap)
                       4'd5:                   w = 8'sd16;
                       default:                w = 8'sd0;
                   endcase
            default: case (tap)
                       4'd1, 4'd3, 4'd7, 4'd9: w = -8'sd1;
                       4'd2, 4'd4, 4'd6, 4'd8: w = -8'sd2;
                       4'd5:                   w = 8'sd28;
                       default:                w = 8'sd0;
                   endcase
        endcase
    end

    always_ff @(posedge clk) begin
        pix_q <= pix;
        w_q   <= w;
    end
    assign prod_full = $signed({1'b0, pix_q}) * w_q;
    assign prod      = prod_full[14:0];
    assign sum       = acc + prod;
    assign acc_clr   = (tap == 4'd0);

    always_ff @(posedge clk) begin
        if (reset | acc_clr) acc <= '0;
        else                 acc <= sum;
    end
endmodule
