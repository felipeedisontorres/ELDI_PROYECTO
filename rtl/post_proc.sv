module post_proc (
    input  logic signed [14:0] acc,
    input  logic               absm,
    output logic [7:0]         y
);
    logic signed [10:0] s;
    logic               neg, big;
    logic [10:0]        negs, a, v;

    assign s    = acc[14:4];
    assign neg  = s[10];
    assign negs = -s;
    assign a    = absm ? negs : 11'd0;
    assign v    = neg  ? a : s;
    assign big  = (v > 11'd255);
    assign y    = big  ? 8'd255 : v[7:0];
endmodule
