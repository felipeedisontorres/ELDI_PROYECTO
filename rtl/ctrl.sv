// ============================================================================
// Bloque 9 - ctrl: unidad de control (FSM Moore + registro MODE + decodificador)
// ----------------------------------------------------------------------------
// FSM de 2 b:  IDLE = 00, P1 = 01, P2 = 10
//   IDLE --(fin | BTNC)--> P1     fin en IDLE = ultimo byte de la imagen recibido
//   P1   --(fin & two_pass)--> P2 --(fin)--> IDLE
//   P1   --(fin & ~two_pass)--> IDLE         fin en P1/P2 = ultimo byte calculado
// IDLE -> P1 solo cambia el bit 0 del estado: BTNC (sin sincronizador ni
// antirrebote, D15/D16) llega a un unico FF de decision.
// MODE (3 b) copia SW[2:0] mientras el estado es IDLE y se congela en P1/P2.
// Decodificador (tabla de verdad del esquematico):
//   estado  MODE        ksel  absm  src_tmp  tmp_wr
//   P1      0 00 (G)     00     0      0       0
//   P1      0 01 (L)     01     1      0       0
//   P1      0 10 (LoG)   00     0      0       1     <- 1a pasada: G -> BRAM_TMP
//   P1      0 11 (US)    11     0      0       0
//   P1      1 xx (byp)   10     0      0       0
//   P2      x xx         01     1      1       0     <- 2a pasada: L sobre BRAM_TMP
// ============================================================================
module ctrl (
    input  logic       clk,
    input  logic       reset,
    input  logic       btnc,                    // pin BTNC (reprocesar)
    input  logic [2:0] sw_mode,                 // SW[2:0] = {bypass, filtro[1:0]}
    input  logic       fin,                     // del contador de posicion: ultimo byte
    output logic [1:0] state,
    output logic [2:0] mode,
    output logic       idle,
    output logic [1:0] ksel,
    output logic       absm,
    output logic       src_tmp,
    output logic       tmp_wr
);
    localparam logic [1:0] IDLE = 2'b00;
    localparam logic [1:0] P1   = 2'b01;
    localparam logic [1:0] P2   = 2'b10;

    logic [1:0] next;
    logic       two_pass;

    // ---------------- registro MODE ----------------
    always_ff @(posedge clk) begin
        if (reset)     mode <= 3'b000;
        else if (idle) mode <= sw_mode;
    end

    // ---------------- FSM: registro de estado ----------------
    (* fsm_encoding = "none" *)
    logic [1:0] state_q;
    always_ff @(posedge clk) begin
        if (reset) state_q <= IDLE;
        else       state_q <= next;
    end
    assign state = state_q;

    // ---------------- FSM: logica de siguiente estado ----------------
    always_comb begin
        case (state_q)
            IDLE:    next = (fin | btnc) ? P1 : IDLE;
            P1:      next = fin ? (two_pass ? P2 : IDLE) : P1;
            P2:      next = fin ? IDLE : P2;
            default: next = IDLE;
        endcase
    end

    // ---------------- decodificador ----------------
    assign idle     = (state_q == IDLE);
    assign two_pass = (mode == 3'b010);          // LoG sin bypass
    assign src_tmp  = (state_q == P2);
    assign tmp_wr   = (state_q == P1) & two_pass;

    assign ksel = (state_q == P2)       ? 2'b01 :     // L sobre el Gaussiano
                  mode[2]               ? 2'b10 :     // bypass -> identidad
                  (mode[1:0] == 2'b11)  ? 2'b11 :     // unsharp
                  (mode[1:0] == 2'b01)  ? 2'b01 :     // Laplaciano
                                          2'b00;      // Gaussiano (G y 1a de LoG)
    assign absm = (ksel == 2'b01);
endmodule
