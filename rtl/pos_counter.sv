// ============================================================================
// Bloque 3 - pos_counter: contador de posicion {ROW, COL, CH} (compartido)
// ----------------------------------------------------------------------------
// El MISMO contador da la direccion de escritura al recibir la imagen (estado
// IDLE, en = wr_in) y el byte que se esta calculando al procesar (P1/P2,
// en = go). Recorre la imagen en el orden en que llega por la UART:
//   fila -> columna -> canal (R, G, B).
// Hardware (igual al esquematico):
//   CH  : contador de 2 b. EN = en, CLR = e_col -> cuenta 0, 1, 2, 0 ...
//   COL : contador de LOG_W b, EN = e_col = en & (CH == 2)
//   ROW : contador de LOG_W b, EN = e_row = e_col & (COL == W-1)
//   fin = e_row & (ROW == W-1): la cuenta avanza DESDE el ultimo byte de la
//         imagen (en IDLE = imagen recibida; en P1/P2 = pasada terminada).
//   COL y ROW vuelven solos a 0 al desbordarse (127 + 1 = 0 en 7 b).
// ============================================================================
module pos_counter #(
    parameter int LOG_W = 7                     // imagen de 2^LOG_W x 2^LOG_W
) (
    input  logic             clk,
    input  logic             reset,
    input  logic             en,                // cnt_en = wr_in | go
    output logic [1:0]       ch,
    output logic [LOG_W-1:0] col,
    output logic [LOG_W-1:0] row,
    output logic             fin                // avanza desde el ultimo byte (fin de imagen)
);
    logic c_ch, col_max, row_max, e_col, e_row;

    assign c_ch    = (ch == 2'd2);               // comparador "= 2"
    assign col_max = (col == '1);                // comparador "= 127"
    assign row_max = (row == '1);                // comparador "= 127"
    assign e_col   = en & c_ch;                  // AND: avanza la columna
    assign e_row   = e_col & col_max;            // AND: avanza la fila
    assign fin     = e_row & row_max;            // AND: fin de la imagen

    always_ff @(posedge clk) begin               // CH: 0, 1, 2, 0 ... (CLR = e_col)
        if (reset | e_col) ch <= 2'd0;
        else if (en)       ch <= ch + 2'd1;
    end

    always_ff @(posedge clk) begin               // COL
        if (reset)      col <= '0;
        else if (e_col) col <= col + 1'b1;
    end

    always_ff @(posedge clk) begin               // ROW
        if (reset)      row <= '0;
        else if (e_row) row <= row + 1'b1;
    end
endmodule
