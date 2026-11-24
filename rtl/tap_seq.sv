module tap_seq #(
    parameter int LOG_W = 7
) (
    input  logic               clk,
    input  logic               reset,
    input  logic               go,
    input  logic               idle,
    input  logic [1:0]         ch,
    input  logic [LOG_W-1:0]   col,
    input  logic [LOG_W-1:0]   row,
    output logic [3:0]         tap,
    output logic               at11,
    output logic [2*LOG_W+1:0] naddr
);
    logic [1:0]       dr, dc;
    logic [LOG_W:0]   rsum, csum;
    logic [LOG_W-1:0] nrow, ncol;
    logic             tap_en;

    assign at11   = (tap == 4'd11);
    assign tap_en = ~(at11 | idle);
    always_ff @(posedge clk) begin
        if (reset | go)  tap <= 4'd0;
        else if (tap_en) tap <= tap + 4'd1;
    end

    always_comb begin
        case (tap)
            4'd0:    {dr, dc} = {2'b11, 2'b11};
            4'd1:    {dr, dc} = {2'b11, 2'b00};
            4'd2:    {dr, dc} = {2'b11, 2'b01};
            4'd3:    {dr, dc} = {2'b00, 2'b11};
            4'd4:    {dr, dc} = {2'b00, 2'b00};
            4'd5:    {dr, dc} = {2'b00, 2'b01};
            4'd6:    {dr, dc} = {2'b01, 2'b11};
            4'd7:    {dr, dc} = {2'b01, 2'b00};
            4'd8:    {dr, dc} = {2'b01, 2'b01};
            default: {dr, dc} = {2'b00, 2'b00};
        endcase
    end

    assign rsum = {1'b0, row} + {{(LOG_W-1){dr[1]}}, dr};
    assign csum = {1'b0, col} + {{(LOG_W-1){dc[1]}}, dc};
    assign nrow = rsum[LOG_W] ? row : rsum[LOG_W-1:0];
    assign ncol = csum[LOG_W] ? col : csum[LOG_W-1:0];

    assign naddr = {nrow, ncol, ch};
endmodule
