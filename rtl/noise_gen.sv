// ============================================================================
// Bloque 2 - noise_gen: ruido sal y pimienta en la FPGA (R-P4, decision D4)
// ----------------------------------------------------------------------------
// Hardware (igual al esquematico):
//   LFSR     : registro de desplazamiento de 16 b con realimentacion XOR
//              (polinomio x^16 + x^14 + x^13 + x^11 + 1, periodo 65 535).
//              lfsr_en = NOR(ch[1], ch[0], wr_in): corre libre mientras se espera
//              el byte R de un pixel y se congela durante R, G y B, asi los tres
//              bytes del pixel usan la MISMA decision (pixel blanco o negro).
//   thr      : umbral = {00, SW[4:3], 0000} = 0, 16, 32 o 48 (solo cables).
//   "<"      : hit = (lfsr[7:0] < thr) -> probabilidad thr/256.
//   MUX_RUIDO: noisy = hit ? {8{lfsr[8]}} : rx_data   (0x00 = pimienta, 0xFF = sal)
// ============================================================================
module noise_gen (
    input  logic       clk,
    input  logic       reset,
    input  logic [1:0] ch,          // canal del byte que llega (0 = R, 1 = G, 2 = B)
    input  logic       wr_in,       // se escribe un byte en BRAM_IN en este ciclo
    input  logic [1:0] level,       // SW[4:3]: densidad 0, 16, 32 o 48 de 256
    input  logic [7:0] din,         // rx_data
    output logic [7:0] noisy        // byte que se escribe en BRAM_IN
);
    logic [15:0] lfsr;
    logic        fb, lfsr_en, hit;
    logic [7:0]  thr;

    assign lfsr_en = ~(ch[1] | ch[0] | wr_in);          // compuerta NOR de 3 entradas
    assign fb      = lfsr[0] ^ lfsr[2] ^ lfsr[3] ^ lfsr[5];

    always_ff @(posedge clk) begin
        if (reset)        lfsr <= 16'hACE1;              // semilla distinta de 0
        else if (lfsr_en) lfsr <= {fb, lfsr[15:1]};
    end

    assign thr   = {2'b00, level, 4'b0000};               // level x 16 (cables)
    assign hit   = (lfsr[7:0] < thr);                     // comparador "<" de 8 b
    assign noisy = hit ? {8{lfsr[8]}} : din;              // MUX 2:1 de 8 b
endmodule
