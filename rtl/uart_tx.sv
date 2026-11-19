// ============================================================================
// Bloque 8 - uart_tx: transmisor UART 8N1
// ----------------------------------------------------------------------------
//   SR_TX   : registro de 10 b con carga paralela (MUX 2:1 carga / desplaza).
//             Carga {1, data, 0} = {parada, dato, inicio}; desplaza a la derecha
//             metiendo 1 por el MSB. tx = SR_TX[0] directo: al terminar, el
//             registro queda en 1s y la linea en reposo (1) sin otro MUX.
//   BIT_TX  : contador descendente de 4 b (bits que faltan). Carga 10 al
//             arrancar y resta 1 en cada tick. tx_busy = (BIT_TX != 0).
//   BAUD_TX : contador mod CLKS_PER_BIT (10 b), borrado cuando ~tx_busy.
//             tick = (BAUD_TX == 867): fin de un bit.
//   Un byte ocupa 10 x 868 = 8 680 ciclos (86,8 us).
//   start solo llega con busy = 0: el control hace go = at11 & ~tx_busy, por eso
//   el transmisor no necesita protegerse (load = start).
// ============================================================================
module uart_tx #(
    parameter int CLKS_PER_BIT = 868
) (
    input  logic       clk,
    input  logic       reset,
    input  logic       start,                   // tx_start (pulso)
    input  logic [7:0] data,                    // y
    output logic       tx,                      // pin UART_RXD_OUT
    output logic       busy                     // tx_busy
);
    localparam int BW   = $clog2(CLKS_PER_BIT);
    localparam int LAST = CLKS_PER_BIT - 1;

    logic [9:0]    sr_tx;
    logic [3:0]    bit_tx;
    logic [BW-1:0] baud_tx;
    logic          tick;

    assign busy = (bit_tx != 4'd0);              // comparador "!= 0"
    assign tick = (baud_tx == LAST[BW-1:0]);     // comparador "= 867"
    assign tx   = sr_tx[0];

    // BAUD_TX: contador mod CLKS_PER_BIT (CLR = ~busy)
    always_ff @(posedge clk) begin
        if (reset | ~busy | tick) baud_tx <= '0;
        else                      baud_tx <= baud_tx + 1'b1;
    end

    // SR_TX y BIT_TX
    always_ff @(posedge clk) begin
        if (reset) begin
            sr_tx  <= '1;                        // linea en reposo = 1
            bit_tx <= 4'd0;
        end else if (start) begin
            sr_tx  <= {1'b1, data, 1'b0};        // {parada, dato, inicio}
            bit_tx <= 4'd10;
        end else if (tick) begin
            sr_tx  <= {1'b1, sr_tx[9:1]};
            bit_tx <= bit_tx - 4'd1;
        end
    end
endmodule
