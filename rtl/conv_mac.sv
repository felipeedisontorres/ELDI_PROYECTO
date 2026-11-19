// ============================================================================
// Bloque 6 - conv_mac: convolucion 3x3 secuencial (multiplicar y acumular)
// ----------------------------------------------------------------------------
// ROM_W : tabla de pesos con direccion {ksel, tap} (6 b) y dato de 8 b con signo.
//         La fila del tap t guarda el peso del pixel que LLEGA de la BRAM en el
//         tap t, es decir, el vecino pedido en el tap t-1 (la BRAM tarda 1 ciclo).
//         Taps 0, 10 y 11 tienen peso 0: en el tap 11 el ACC se mantiene solo.
//         Todos los kernels estan multiplicados por 16 para que la
//         normalizacion sea SIEMPRE /16 (solo cables en post_proc):
//           ksel 00  Gaussiano  [ 1  2  1;  2   4  2;  1  2  1]          (/16)
//           ksel 01  Laplaciano [ 0 16  0; 16 -64 16;  0 16  0] = 16*L  (/16)
//           ksel 10  Identidad  [ 0  0  0;  0  16  0;  0  0  0] = bypass(/16)
//           ksel 11  Unsharp    [-1 -2 -1; -2  28 -2; -1 -2 -1] = 32*I - G (/16)
// REG_PIX, REG_W (registro de segmentacion, v4.1): pix y w se registran antes
//         del multiplicador. Asi el camino BRAM -> multiplicador -> sumador
//         -> ACC (11,35 ns en Vivado, no cabia en 10 ns) se parte en dos:
//         BRAM -> REG_PIX y REG_PIX -> X -> + -> ACC. Cada producto entra al
//         ACC un tap despues; el resultado completo esta listo en el tap 11.
// "X"   : multiplicador con signo {0,pix} (9 b) x w (8 b). |w*pix| <= 64*255 =
//         16 320 < 2^14 -> el producto cabe en 15 b con signo.
// "+"   : sum = acc + prod (15 b). ACC: registro de 15 b con borrado sincrono
//         cuando tap = 0 (comparador "= 0" sobre el bus tap). En IDLE el TAP esta
//         en 0, asi que el ACC queda en 0 sin otra senal de control.
//         Rango total: -16 320 <= acc <= 16 320 (caso Laplaciano) -> 15 b.
// ============================================================================
module conv_mac (
    input  logic               clk,
    input  logic               reset,
    input  logic [1:0]         ksel,            // kernel elegido por el control
    input  logic [3:0]         tap,
    input  logic [7:0]         pix,             // byte leido de BRAM_IN o BRAM_TMP
    output logic signed [14:0] acc
);
    logic signed [7:0]  w, w_q;                  // peso de la ROM y peso registrado
    logic        [7:0]  pix_q;                   // pixel registrado (REG_PIX)
    logic signed [16:0] prod_full;               // bits 16:15 = solo signo (no se usan)
    logic signed [14:0] prod, sum;
    logic               acc_clr;

    // ---------------- ROM_W (64 x 8 b; se usan 4 x 12) ----------------
    always_comb begin
        w = 8'sd0;
        case (ksel)
            2'b00: case (tap)                    // Gaussiano
                       4'd1, 4'd3, 4'd7, 4'd9: w = 8'sd1;    // esquinas
                       4'd2, 4'd4, 4'd6, 4'd8: w = 8'sd2;    // lados
                       4'd5:                   w = 8'sd4;    // centro
                       default:                w = 8'sd0;
                   endcase
            2'b01: case (tap)                    // Laplaciano x 16
                       4'd2, 4'd4, 4'd6, 4'd8: w = 8'sd16;
                       4'd5:                   w = -8'sd64;
                       default:                w = 8'sd0;
                   endcase
            2'b10: case (tap)                    // Identidad x 16 (bypass)
                       4'd5:                   w = 8'sd16;
                       default:                w = 8'sd0;
                   endcase
            default: case (tap)                  // Unsharp x 16 = 32*I - G
                       4'd1, 4'd3, 4'd7, 4'd9: w = -8'sd1;
                       4'd2, 4'd4, 4'd6, 4'd8: w = -8'sd2;
                       4'd5:                   w = 8'sd28;
                       default:                w = 8'sd0;
                   endcase
        endcase
    end

    // ---------------- registro de segmentacion (REG_PIX, REG_W) ----------------
    always_ff @(posedge clk) begin
        pix_q <= pix;
        w_q   <= w;
    end
    // ---------------- multiplicador, sumador y acumulador ----------------
    assign prod_full = $signed({1'b0, pix_q}) * w_q;  // 9 b x 8 b con signo
    assign prod      = prod_full[14:0];           // cabe en 15 b (ver arriba)
    assign sum       = acc + prod;
    assign acc_clr   = (tap == 4'd0);             // comparador "= 0"

    always_ff @(posedge clk) begin
        if (reset | acc_clr) acc <= '0;
        else                 acc <= sum;
    end
endmodule
