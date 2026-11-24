module pos_counter #(
    parameter int LOG_W = 7
) (
    input  logic             clk,
    input  logic             reset,
    input  logic             en,
    output logic [1:0]       ch,
    output logic [LOG_W-1:0] col,
    output logic [LOG_W-1:0] row,
    output logic             fin
);
    logic c_ch, col_max, row_max, e_col, e_row;

    assign c_ch    = (ch == 2'd2);
    assign col_max = (col == '1);
    assign row_max = (row == '1);
    assign e_col   = en & c_ch;
    assign e_row   = e_col & col_max;
    assign fin     = e_row & row_max;

    always_ff @(posedge clk) begin
        if (reset | e_col) ch <= 2'd0;
        else if (en)       ch <= ch + 2'd1;
    end

    always_ff @(posedge clk) begin
        if (reset)      col <= '0;
        else if (e_col) col <= col + 1'b1;
    end

    always_ff @(posedge clk) begin
        if (reset)      row <= '0;
        else if (e_row) row <= row + 1'b1;
    end
endmodule
