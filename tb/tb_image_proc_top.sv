// ============================================================================
// tb_image_proc_top: testbench del SISTEMA completo (todos los bloques juntos)
// ----------------------------------------------------------------------------
// La imagen entra bit a bit por el pin UART_TXD_IN y la respuesta se decodifica
// bit a bit desde el pin UART_RXD_OUT, igual que en la tarjeta. Cada byte
// recibido se compara con un MODELO DE REFERENCIA escrito aqui (convolucion
// 3x3 con borde replicado, /16 por piso, |.| o recorte, saturacion a 255).
// El modelo vive SOLO en el testbench (verificacion), no en el sistema (R-F01).
//
// FULL = 0 (por defecto): imagen 8 x 8, CPB = 8. Casos: G, L, LoG, Unsharp,
//   bypass (100 y 111) con BTNC, imagen de extremos, ruido en los 3 niveles
//   (estructura, densidad y contenido exacto de BRAM_IN), filtros sobre la
//   imagen con ruido, bytes que llegan durante el procesamiento (se ignoran),
//   BTNC sostenido durante el procesamiento (se ignora), LEDs, contenido de
//   BRAM_TMP en el LoG y temporizacion de la salida.
// FULL = 1: imagen real de 128 x 128 leida de img_in.hex; corre todos los modos
//   y guarda cada salida en out_<modo>.hex (para las figuras del informe).
// ============================================================================
`timescale 1ns/1ps
module tb_image_proc_top;
    parameter int LOG_W = 3;
    parameter int CPB   = 8;
    parameter int FULL  = 0;
    localparam int W  = 1 << LOG_W;
    localparam int NB = W * W * 3;               // bytes por imagen

    logic       CLK100MHZ = 0, CPU_RESETN = 0, UART_TXD_IN = 1, BTNC = 0;
    logic [4:0] SW = 5'b00000;
    logic       UART_RXD_OUT;
    logic [7:0] LED;

    image_proc_top #(.CLKS_PER_BIT(CPB), .LOG_W(LOG_W)) dut (
        .CLK100MHZ(CLK100MHZ), .CPU_RESETN(CPU_RESETN), .UART_TXD_IN(UART_TXD_IN),
        .UART_RXD_OUT(UART_RXD_OUT), .SW(SW), .BTNC(BTNC), .LED(LED));

    always #5 CLK100MHZ = ~CLK100MHZ;            // 100 MHz

    integer errors = 0, checks = 0;
    integer cyc = 0;
    always @(posedge CLK100MHZ) cyc <= cyc + 1;

    // ---------------- memorias del testbench ----------------
    logic [7:0] img    [0:NB-1];                 // imagen enviada
    logic [7:0] stored [0:NB-1];                 // contenido esperado de BRAM_IN (con ruido)
    logic [7:0] tmpimg [0:NB-1];                 // Gaussiano esperado (1a pasada LoG)
    logic [7:0] refo   [0:NB-1];                 // salida esperada
    logic [7:0] outb   [0:NB-1];                 // salida recibida
    integer     out_cnt = 0;
    integer     K [0:3][0:8];

    // ================= UART: envio de bytes al pin UART_TXD_IN =================
    task automatic send_byte(input [7:0] b);
        integer i;
        begin
            @(negedge CLK100MHZ); UART_TXD_IN = 1'b0;
            repeat (CPB) @(negedge CLK100MHZ);
            for (i = 0; i < 8; i = i + 1) begin
                UART_TXD_IN = b[i];
                repeat (CPB) @(negedge CLK100MHZ);
            end
            UART_TXD_IN = 1'b1;
            repeat (CPB) @(negedge CLK100MHZ);
        end
    endtask

    task automatic send_image;
        integer i;
        begin
            wr_cnt = 0;
            for (i = 0; i < NB; i = i + 1) send_byte(img[i]);
        end
    endtask

    // ================= UART: decodificacion del pin UART_RXD_OUT =================
    integer tx_t0 = 0, tx_prev = 0, tx_gap_min = 1 << 30, tx_gap_max = 0;
    always begin : monitor_tx
        logic [7:0] b;
        integer i;
        @(negedge UART_RXD_OUT);
        if (out_cnt == 0) tx_t0 = cyc;
        else begin
            if (cyc - tx_prev < tx_gap_min) tx_gap_min = cyc - tx_prev;
            if (cyc - tx_prev > tx_gap_max) tx_gap_max = cyc - tx_prev;
        end
        tx_prev = cyc;
        repeat (CPB/2) @(posedge CLK100MHZ);
        if (UART_RXD_OUT !== 1'b0) begin errors = errors + 1; $display("ERROR: bit de inicio falso"); end
        for (i = 0; i < 8; i = i + 1) begin
            repeat (CPB) @(posedge CLK100MHZ);
            b[i] = UART_RXD_OUT;
        end
        repeat (CPB) @(posedge CLK100MHZ);
        if (UART_RXD_OUT !== 1'b1) begin errors = errors + 1; $display("ERROR: bit de parada = 0"); end
        if (out_cnt < NB) outb[out_cnt] = b;
        out_cnt = out_cnt + 1;
    end

    // ================= modelo del ruido (LFSR) =================
    // Se replica el LFSR; el enable usa ch y wr_in del DUT (verificados aparte).
    logic [15:0] m_lfsr;
    integer      wr_cnt = 0, hit_px = 0;
    logic        m_hit;
    always @(posedge CLK100MHZ) begin
        if (!CPU_RESETN) m_lfsr <= 16'hACE1;
        else begin
            if (dut.wr_in) begin
                m_hit = (m_lfsr[7:0] < SW[4:3] * 16);
                stored[wr_cnt] = m_hit ? {8{m_lfsr[8]}} : img[wr_cnt];
                if (m_hit && dut.ch == 2'd0) hit_px = hit_px + 1;
                wr_cnt = wr_cnt + 1;
            end
            if (dut.ch == 2'd0 && !dut.wr_in)
                m_lfsr <= {m_lfsr[0] ^ m_lfsr[2] ^ m_lfsr[3] ^ m_lfsr[5], m_lfsr[15:1]};
        end
    end

    // ================= modelo de referencia de los filtros =================
    function automatic integer clampi(input integer v);
        clampi = (v < 0) ? 0 : (v > W-1) ? W-1 : v;
    endfunction

    // k: 0 G, 1 L, 2 identidad, 3 unsharp.  src: 0 stored, 1 tmpimg.  dst: 0 refo, 1 tmpimg
    task automatic conv_ref(input integer k, input integer src, input integer dst);
        integer r, c, chn, i, acc, s, e, v;
        begin
            for (r = 0; r < W; r = r + 1)
                for (c = 0; c < W; c = c + 1)
                    for (chn = 0; chn < 3; chn = chn + 1) begin
                        acc = 0;
                        for (i = 0; i < 9; i = i + 1) begin
                            if (src == 0) v = stored[(clampi(r + i/3 - 1)*W + clampi(c + i%3 - 1))*3 + chn];
                            else          v = tmpimg[(clampi(r + i/3 - 1)*W + clampi(c + i%3 - 1))*3 + chn];
                            acc = acc + K[k][i] * v;
                        end
                        s = acc >>> 4;                       // piso de acc/16
                        if (s < 0) e = (k == 1) ? -s : 0; else e = s;
                        if (e > 255) e = 255;
                        if (dst == 0) refo[(r*W + c)*3 + chn] = e;
                        else          tmpimg[(r*W + c)*3 + chn] = e;
                    end
        end
    endtask

    // modo = SW[2:0]
    task automatic make_ref(input [2:0] md);
        begin
            if (md[2])               conv_ref(2, 0, 0);       // bypass
            else case (md[1:0])
                2'b00: conv_ref(0, 0, 0);                     // G
                2'b01: conv_ref(1, 0, 0);                     // L
                2'b10: begin conv_ref(0, 0, 1); conv_ref(1, 1, 0); end   // LoG
                2'b11: conv_ref(3, 0, 0);                     // unsharp
            endcase
        end
    endtask

    // ================= utilidades de verificacion =================
    task automatic wait_output(input integer timeout_cycles);
        integer t;
        begin
            t = 0;
            while (out_cnt < NB && t < timeout_cycles) begin @(posedge CLK100MHZ); t = t + 1; end
            repeat (12*CPB) @(posedge CLK100MHZ);              // margen: no deben llegar mas bytes
        end
    endtask

    task automatic compare_output(input [2:0] md, input [8*8-1:0] name);
        integer i, bad;
        begin
            make_ref(md);
            bad = 0;
            checks = checks + 1;
            if (out_cnt != NB) begin
                errors = errors + 1;
                $display("ERROR %0s: llegaron %0d bytes de %0d", name, out_cnt, NB);
            end
            for (i = 0; i < NB; i = i + 1) begin
                checks = checks + 1;
                if (outb[i] !== refo[i]) begin
                    bad = bad + 1; errors = errors + 1;
                    if (bad <= 5) $display("ERROR %0s: byte %0d = %0d, esperado %0d", name, i, outb[i], refo[i]);
                end
            end
            $display("  %-8s: %0d/%0d bytes iguales al modelo; salida en %0d ciclos (separacion %0d..%0d ciclos)",
                     name, NB - bad, NB, cyc - tx_t0, tx_gap_min, tx_gap_max);
        end
    endtask

    task automatic start_btnc(input [2:0] md);
        begin
            @(negedge CLK100MHZ); SW[2:0] = md;
            repeat (3) @(negedge CLK100MHZ);
            out_cnt = 0; tx_gap_min = 1 << 30; tx_gap_max = 0;
            BTNC = 1; repeat (20) @(negedge CLK100MHZ); BTNC = 0;   // pulsacion "larga"
        end
    endtask

    task automatic check_bram_in;
        integer r, c, chn, bad;
        begin
            bad = 0;
            for (r = 0; r < W; r = r + 1)
                for (c = 0; c < W; c = c + 1)
                    for (chn = 0; chn < 3; chn = chn + 1) begin
                        checks = checks + 1;
                        if (dut.u_bram_in.mem[(r << (LOG_W + 2)) | (c << 2) | chn] !== stored[(r*W + c)*3 + chn]) begin
                            bad = bad + 1; errors = errors + 1;
                        end
                    end
            if (bad) $display("ERROR: BRAM_IN difiere en %0d posiciones", bad);
        end
    endtask

    task automatic dump_out(input [8*16-1:0] fname);
        integer f, i;
        begin
            f = $fopen(fname, "w");
            for (i = 0; i < NB; i = i + 1) $fwrite(f, "%02x\n", outb[i]);
            $fclose(f);
        end
    endtask

    integer i, j, t_pass, f;
    integer hits, bad_px;
    integer timeout;
    initial begin
        // tablas de pesos (orden de barrido)
        for (i = 0; i < 9; i = i + 1) begin K[0][i] = 0; K[1][i] = 0; K[2][i] = 0; K[3][i] = 0; end
        K[0][0]=1;  K[0][1]=2;  K[0][2]=1;  K[0][3]=2;  K[0][4]=4;   K[0][5]=2;  K[0][6]=1;  K[0][7]=2;  K[0][8]=1;
        K[1][1]=16; K[1][3]=16; K[1][4]=-64; K[1][5]=16; K[1][7]=16;
        K[2][4]=16;
        K[3][0]=-1; K[3][1]=-2; K[3][2]=-1; K[3][3]=-2; K[3][4]=28;  K[3][5]=-2; K[3][6]=-1; K[3][7]=-2; K[3][8]=-1;
        timeout = NB * (10*CPB + 20) * 2 + 100000;

`ifdef DUMP
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_image_proc_top);
`endif
        repeat (5) @(negedge CLK100MHZ);
        CPU_RESETN = 1;
        repeat (20) @(negedge CLK100MHZ);
        checks = checks + 1;
        if (LED !== 8'h00) begin errors = errors + 1; $display("ERROR: LED tras reset = %h", LED); end

        if (FULL == 0) begin
            // ---------- 1) imagen aleatoria, Gaussiano ----------
            for (i = 0; i < NB; i = i + 1) img[i] = $urandom % 256;
            SW = 5'b00_000; out_cnt = 0;
            send_image;
            wait_output(timeout);
            check_bram_in;
            compare_output(3'b000, "G");
            // ---------- 2) BTNC: L, LoG, Unsharp, bypass ----------
            start_btnc(3'b001); wait_output(timeout); compare_output(3'b001, "L");
            start_btnc(3'b010);
            // LEDs y BRAM_TMP durante el LoG
            wait (dut.state == 2'b10);
            checks = checks + 1;
            if (LED !== {2'b10, 3'b000, 3'b010}) begin errors = errors + 1; $display("ERROR: LED en P2 = %b", LED); end
            conv_ref(0, 0, 1);
            for (i = 0; i < W*W*3; i = i + 1) begin
                checks = checks + 1;
                if (dut.u_bram_tmp.mem[((i/3/W) << (LOG_W + 2)) | (((i/3)%W) << 2) | (i%3)] !== tmpimg[i]) begin
                    errors = errors + 1; $display("ERROR: BRAM_TMP[%0d]", i);
                end
            end
            wait_output(timeout); compare_output(3'b010, "LoG");
            start_btnc(3'b011);
            @(negedge CLK100MHZ);
            checks = checks + 1;
            if (LED !== {2'b01, 3'b000, 3'b011}) begin errors = errors + 1; $display("ERROR: LED en P1 = %b", LED); end
            // BTNC sostenido durante el procesamiento: no debe reiniciar nada
            BTNC = 1; repeat (300) @(negedge CLK100MHZ); BTNC = 0;
            wait_output(timeout); compare_output(3'b011, "US");
            start_btnc(3'b100); wait_output(timeout); compare_output(3'b100, "bypass");
            start_btnc(3'b111); wait_output(timeout); compare_output(3'b111, "byp111");

            // ---------- 3) imagen de extremos (bordes fuertes, saturacion) ----------
            for (i = 0; i < W*W; i = i + 1)
                for (j = 0; j < 3; j = j + 1)
                    img[i*3 + j] = (((i / W) + (i % W)) % 2) ? 8'hFF : 8'h00;   // damero
            img[(W+1)*3] = 8'h80; img[NB-1] = 8'hFF; img[0] = 8'h00;
            SW = 5'b00_001; out_cnt = 0; tx_gap_min = 1 << 30; tx_gap_max = 0;
            send_image; wait_output(timeout); check_bram_in;
            compare_output(3'b001, "L-ext");
            start_btnc(3'b010); wait_output(timeout); compare_output(3'b010, "LoG-ext");
            start_btnc(3'b011); wait_output(timeout); compare_output(3'b011, "US-ext");
            start_btnc(3'b000); wait_output(timeout); compare_output(3'b000, "G-ext");

            // ---------- 4) ruido en los 3 niveles ----------
            for (j = 1; j < 4; j = j + 1) begin
                for (i = 0; i < NB; i = i + 1) img[i] = 8'd60 + ($urandom % 136);   // sin 0 ni 255
                SW = {j[1:0], 3'b100}; out_cnt = 0; hit_px = 0; tx_gap_min = 1 << 30; tx_gap_max = 0;
                send_image; wait_output(timeout); check_bram_in;
                compare_output(3'b100, "ruido");
                // estructura: cada pixel intacto o los 3 canales a 0x00 / 0xFF
                hits = 0; bad_px = 0;
                for (i = 0; i < W*W; i = i + 1) begin
                    if (outb[i*3] == img[i*3] && outb[i*3+1] == img[i*3+1] && outb[i*3+2] == img[i*3+2]) ;
                    else if ((outb[i*3] == 8'h00 && outb[i*3+1] == 8'h00 && outb[i*3+2] == 8'h00) ||
                             (outb[i*3] == 8'hFF && outb[i*3+1] == 8'hFF && outb[i*3+2] == 8'hFF)) hits = hits + 1;
                    else bad_px = bad_px + 1;
                end
                checks = checks + 1;
                if (bad_px != 0 || hits != hit_px) begin
                    errors = errors + 1; $display("ERROR: ruido mal formado (%0d malos)", bad_px);
                end
                $display("    nivel %0d: %0d de %0d pixeles con ruido (esperado ~%0d)", j, hits, W*W, (W*W*16*j)/256);
                start_btnc(3'b000); wait_output(timeout); compare_output(3'b000, "G-ruido");
            end

            // ---------- 5) bytes que llegan durante el procesamiento se ignoran ----------
            start_btnc(3'b011);
            repeat (40*CPB) @(negedge CLK100MHZ);
            send_byte(8'h77); send_byte(8'h88);
            checks = checks + 1;
            if (dut.wr_in !== 1'b0) begin errors = errors + 1; end
            wait_output(timeout); compare_output(3'b011, "US+rx");
            checks = checks + 1;
            if ({dut.row, dut.col, dut.ch} !== '0) begin errors = errors + 1; $display("ERROR: posicion no volvio a 0"); end
        end else begin
            // ===================== imagen real de 128 x 128 =====================
            $readmemh("img_in.hex", img);
            SW = 5'b00_000; out_cnt = 0;
            send_image; wait_output(timeout); check_bram_in;
            compare_output(3'b000, "G");        dump_out("out_G.hex");
            start_btnc(3'b001); wait_output(timeout); compare_output(3'b001, "L");      dump_out("out_L.hex");
            start_btnc(3'b010); wait_output(timeout); compare_output(3'b010, "LoG");    dump_out("out_LoG.hex");
            start_btnc(3'b011); wait_output(timeout); compare_output(3'b011, "US");     dump_out("out_US.hex");
            start_btnc(3'b100); wait_output(timeout); compare_output(3'b100, "bypass"); dump_out("out_BYP.hex");
            // misma imagen con ruido nivel 2 (12,5 %)
            SW = 5'b10_100; out_cnt = 0; hit_px = 0; tx_gap_min = 1 << 30; tx_gap_max = 0;
            send_image; wait_output(timeout); check_bram_in;
            compare_output(3'b100, "ruido");    dump_out("out_NOISE.hex");
            $display("    %0d de %0d pixeles con ruido", hit_px, W*W);
            start_btnc(3'b000); wait_output(timeout); compare_output(3'b000, "G-ruido"); dump_out("out_NG.hex");
            start_btnc(3'b010); wait_output(timeout); compare_output(3'b010, "LoG-ruid"); dump_out("out_NLoG.hex");
        end

        $display("TB tb_image_proc_top (W=%0d, CPB=%0d): %0d verificaciones, %0d errores -> %s",
                 W, CPB, checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
