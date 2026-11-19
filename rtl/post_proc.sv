// ============================================================================
// Bloque 7 - post_proc: normalizacion, valor absoluto / recorte y saturacion
// ----------------------------------------------------------------------------
//   s     = acc / 16 = acc[14:4]  (desplazamiento aritmetico: SOLO CABLES), 11 b
//   neg   = s[10] (bit de signo)  equivale al comparador "s < 0"
//   MUX_A : absm ? -s : 0         (Laplaciano: |s|  /  resto: negativos a 0)
//   MUX_B : neg  ? MUX_A : s      -> v (11 b, 0..1024)
//   ">"   : big = (v > 255)
//   MUX_SAT: big ? 255 : v[7:0]   -> y (8 b)
// Resultado por kernel:  G y bypass: s >= 0 siempre;  L y LoG: |s| saturado a
// 255 (D2);  Unsharp: s recortado a 0..255 (D3).
// Se usan 11 b en todo el bloque para que sea correcto con CUALQUIER valor de
// 15 b del ACC (incluso -16 384, que el diseno nunca produce: el minimo real es
// -16 320). Asi el testbench puede ser exhaustivo.
// ============================================================================
module post_proc (
    input  logic signed [14:0] acc,             // acc[3:0] se descartan (/16)
    input  logic               absm,            // 1 = valor absoluto (kernel L)
    output logic [7:0]         y
);
    logic signed [10:0] s;
    logic               neg, big;
    logic [10:0]        negs, a, v;

    assign s    = acc[14:4];                     // /16 (cables)
    assign neg  = s[10];
    assign negs = -s;                            // 0 - s (11 b)
    assign a    = absm ? negs : 11'd0;           // MUX_A
    assign v    = neg  ? a : s;                  // MUX_B
    assign big  = (v > 11'd255);                 // comparador "> 255"
    assign y    = big  ? 8'd255 : v[7:0];        // MUX_SAT (saturacion)
endmodule
