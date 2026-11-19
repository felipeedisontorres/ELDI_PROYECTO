// ============================================================================
// Bloque 5 - tap_seq: secuenciador de taps y direccion del vecino (con bordes)
// ----------------------------------------------------------------------------
// TAP     : contador de 4 b. CLR = go (byte terminado) y EN = NOR(at11, idle):
//           cuenta 0..11 y se queda en 11 hasta que llega go; en IDLE no cuenta
//           (queda en 0, porque el ultimo go de la pasada lo dejo en 0).
// ROM_OFF : tabla tap -> (dr, dc) en complemento a 2 de 2 b (-1 = 11, 0 = 00,
//           +1 = 01). Taps 0..8 = vecinos en orden de barrido; 9, 10 y 11 = centro.
// Bordes  : se replica el borde (D1). Sumador de LOG_W+1 b: si el MSB de la suma
//           sale en 1, el vecino esta fuera de 0..W-1 (-1 o W) y el MUX deja la
//           coordenada actual ("si se sale, no se mueve").
// naddr   : {nrow, ncol, ch} -> direccion de lectura de BRAM_IN y BRAM_TMP.
// ============================================================================
module tap_seq #(
    parameter int LOG_W = 7
) (
    input  logic               clk,
    input  logic               reset,
    input  logic               go,              // byte entregado: vuelve a 0
    input  logic               idle,            // estado IDLE: no cuenta
    input  logic [1:0]         ch,
    input  logic [LOG_W-1:0]   col,
    input  logic [LOG_W-1:0]   row,
    output logic [3:0]         tap,
    output logic               at11,            // tap == 11: resultado listo
    output logic [2*LOG_W+1:0] naddr
);
    logic [1:0]       dr, dc;
    logic [LOG_W:0]   rsum, csum;               // LOG_W+1 bits
    logic [LOG_W-1:0] nrow, ncol;
    logic             tap_en;

    // ---------------- contador TAP ----------------
    assign at11   = (tap == 4'd11);             // comparador "= 11"
    assign tap_en = ~(at11 | idle);             // compuerta NOR
    always_ff @(posedge clk) begin
        if (reset | go)  tap <= 4'd0;
        else if (tap_en) tap <= tap + 4'd1;
    end

    // ---------------- ROM_OFF (12 x 4 b) ----------------
    always_comb begin
        case (tap)
            4'd0:    {dr, dc} = {2'b11, 2'b11};  // (-1,-1)
            4'd1:    {dr, dc} = {2'b11, 2'b00};  // (-1, 0)
            4'd2:    {dr, dc} = {2'b11, 2'b01};  // (-1,+1)
            4'd3:    {dr, dc} = {2'b00, 2'b11};  // ( 0,-1)
            4'd4:    {dr, dc} = {2'b00, 2'b00};  // ( 0, 0)
            4'd5:    {dr, dc} = {2'b00, 2'b01};  // ( 0,+1)
            4'd6:    {dr, dc} = {2'b01, 2'b11};  // (+1,-1)
            4'd7:    {dr, dc} = {2'b01, 2'b00};  // (+1, 0)
            4'd8:    {dr, dc} = {2'b01, 2'b01};  // (+1,+1)
            default: {dr, dc} = {2'b00, 2'b00};  // 9, 10, 11: centro
        endcase
    end

    // ---------------- vecino con borde replicado ----------------
    // Sumadores de LOG_W+1 b: {0, fila} + extension de signo de dr
    assign rsum = {1'b0, row} + {{(LOG_W-1){dr[1]}}, dr};
    assign csum = {1'b0, col} + {{(LOG_W-1){dc[1]}}, dc};
    // MUX 2:1: si el MSB es 1 (se sale), se queda en la fila/columna actual
    assign nrow = rsum[LOG_W] ? row : rsum[LOG_W-1:0];
    assign ncol = csum[LOG_W] ? col : csum[LOG_W-1:0];

    assign naddr = {nrow, ncol, ch};
endmodule
