module image_proc_top #(
    parameter int CLKS_PER_BIT = 868,
    parameter int LOG_W        = 7
) (
    input  logic       CLK100MHZ,
    input  logic       CPU_RESETN,
    input  logic       UART_TXD_IN,
    output logic       UART_RXD_OUT,
    input  logic [4:0] SW,
    input  logic       BTNC,
    output logic [7:0] LED
);
    localparam int AW = 2*LOG_W + 2;

    logic             clk, reset;
    logic             rx_valid;
    logic [7:0]       rx_data;
    logic [7:0]       noisy;
    logic [7:0]       dout_in, dout_tmp, pix;
    logic [1:0]       ch;
    logic [LOG_W-1:0] col, row;
    logic [AW-1:0]    pos;
    logic [3:0]       tap;
    logic             at11;
    logic [AW-1:0]    naddr;
    logic signed [14:0] acc;
    logic [7:0]       y;
    logic             tx_busy;
    logic [1:0]       state, ksel;
    logic [2:0]       mode;
    logic             idle, absm, src_tmp, tmp_wr;
    logic             wr_in, go, cnt_en, fin, tx_start, we_tmp;

    assign clk   = CLK100MHZ;
    assign reset = ~CPU_RESETN;

    assign wr_in    = rx_valid & idle;
    assign go       = at11 & ~tx_busy;
    assign cnt_en   = wr_in | go;
    assign tx_start = go & ~tmp_wr;
    assign we_tmp   = tmp_wr;
    assign pos      = {row, col, ch};
    assign pix      = src_tmp ? dout_tmp : dout_in;
    assign LED      = {state, 3'b000, mode};

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
