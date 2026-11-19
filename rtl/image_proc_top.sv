// ============================================================================
// image_proc_top - Proyecto #8 Image Processor (2D filters), arquitectura v4.1
// Nexys A7-100T (XC7A100T), reloj de 100 MHz, UART 115200 8N1.
// ----------------------------------------------------------------------------
// El PC envia 128 x 128 pixeles RGB (49 152 bytes, fila por fila, R G B).
// La FPGA los guarda (con ruido opcional), aplica el filtro elegido con SW y
// devuelve 49 152 bytes. BTNC reprocesa la misma imagen sin reenviarla.
//   SW[1:0] filtro: 00 Gaussiano, 01 Laplaciano, 10 LoG, 11 Unsharp
//   SW[2]   bypass (devuelve la imagen recibida, con ruido si lo hay)
//   SW[4:3] densidad de ruido: 0, 16, 32, 48 de 256 (0 %, 6,25 %, 12,5 %, 18,75 %)
//   LED[2:0] = MODE (modo congelado)    LED[7:6] = estado (00 IDLE, 01 P1, 10 P2)
// Procesamiento byte a byte (un canal a la vez): 12 ciclos por byte + espera
// de la UART. Todo el datapath es de 8 b de entrada y salida.
// Los nombres de las senales son los mismos del esquematico.
// ============================================================================
module image_proc_top #(
    parameter int CLKS_PER_BIT = 868,           // 100 MHz / 115200
    parameter int LOG_W        = 7              // 128 x 128 (8 x 8 en simulacion rapida)
) (
    input  logic       CLK100MHZ,
    input  logic       CPU_RESETN,              // activo en bajo
    input  logic       UART_TXD_IN,             // datos del PC hacia la FPGA
    output logic       UART_RXD_OUT,            // datos de la FPGA hacia el PC
    input  logic [4:0] SW,
    input  logic       BTNC,
    output logic [7:0] LED
);
    localparam int AW = 2*LOG_W + 2;            // 16 b: {fila, columna, canal}

    logic             clk, reset;
    // UART RX
    logic             rx_valid;
    logic [7:0]       rx_data;
    // ruido y memoria de entrada
    logic [7:0]       noisy;
    logic [7:0]       dout_in, dout_tmp, pix;
    // posicion
    logic [1:0]       ch;
    logic [LOG_W-1:0] col, row;
    logic [AW-1:0]    pos;
    // secuenciador
    logic [3:0]       tap;
    logic             at11;
    logic [AW-1:0]    naddr;
    // datapath
    logic signed [14:0] acc;
    logic [7:0]       y;
    // UART TX
    logic             tx_busy;
    // control
    logic [1:0]       state, ksel;
    logic [2:0]       mode;
    logic             idle, absm, src_tmp, tmp_wr;
    logic             wr_in, go, cnt_en, fin, tx_start, we_tmp;

    assign clk   = CLK100MHZ;
    assign reset = ~CPU_RESETN;                  // inversor

    // ---------------- logica de pegado (compuertas del bloque 9) ----------------
    assign wr_in    = rx_valid & idle;           // solo se recibe en IDLE
    assign go       = at11 & ~tx_busy;           // byte listo y TX libre
    assign cnt_en   = wr_in | go;                // avanza la posicion
    assign tx_start = go & ~tmp_wr;              // enviar y por la UART
    assign we_tmp   = tmp_wr;                    // BRAM_TMP se escribe en toda la 1a pasada
                                                 // del LoG: la ultima escritura de cada
                                                 // posicion (en el ciclo de go) es la buena
    assign pos      = {row, col, ch};
    assign pix      = src_tmp ? dout_tmp : dout_in;   // MUX_SRC
    assign LED      = {state, 3'b000, mode};

    // ---------------- bloques ----------------
    uart_rx #(.CLKS_PER_BIT(CLKS_PER_BIT)) u_rx (
        .clk(clk), .reset(reset), .rx(UART_TXD_IN),
        .rx_valid(rx_valid), .rx_data(rx_data));

    noise_gen u_noise (
        .clk(clk), .reset(reset), .ch(ch), .wr_in(wr_in), .level(SW[4:3]),
        .din(rx_data), .noisy(noisy));

    pos_counter #(.LOG_W(LOG_W)) u_pos (
        .clk(clk), .reset(reset), .en(cnt_en),
        .ch(ch), .col(col), .row(row), .fin(fin));

    bram_sdp #(.AW(AW), .DW(8)) u_bram_in (
        .clk(clk), .we(wr_in), .waddr(pos), .din(noisy),
        .raddr(naddr), .dout(dout_in));

    bram_sdp #(.AW(AW), .DW(8)) u_bram_tmp (
        .clk(clk), .we(we_tmp), .waddr(pos), .din(y),
        .raddr(naddr), .dout(dout_tmp));

    tap_seq #(.LOG_W(LOG_W)) u_tap (
        .clk(clk), .reset(reset), .go(go), .idle(idle), .ch(ch), .col(col), .row(row),
        .tap(tap), .at11(at11), .naddr(naddr));

    conv_mac u_mac (
        .clk(clk), .reset(reset), .ksel(ksel), .tap(tap),
        .pix(pix), .acc(acc));

    post_proc u_post (
        .acc(acc), .absm(absm), .y(y));

    uart_tx #(.CLKS_PER_BIT(CLKS_PER_BIT)) u_tx (
        .clk(clk), .reset(reset), .start(tx_start), .data(y),
        .tx(UART_RXD_OUT), .busy(tx_busy));

    ctrl u_ctrl (
        .clk(clk), .reset(reset), .btnc(BTNC), .sw_mode(SW[2:0]), .fin(fin),
        .state(state), .mode(mode), .idle(idle), .ksel(ksel), .absm(absm),
        .src_tmp(src_tmp), .tmp_wr(tmp_wr));
endmodule
