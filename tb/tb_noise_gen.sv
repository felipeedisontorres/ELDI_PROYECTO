// ============================================================================
// tb_noise_gen: testbench autoverificable del generador de ruido (bloque 2)
// Casos: periodo del LFSR = 65 535 y nunca 0; numero EXACTO de aciertos por
// nivel en un periodo (0, 4095, 8191, 12 287); salida = modelo independiente
// en cada ciclo con entradas aleatorias; los 3 bytes de un pixel reciben la
// misma decision (LFSR congelado); nivel 0 = sin ruido.
// ============================================================================
`timescale 1ns/1ps
module tb_noise_gen;
    logic       clk = 0, reset = 1;
    logic [1:0] ch = 0, level = 0;
    logic       wr_in = 0;
    logic [7:0] din = 0, noisy;

    noise_gen dut (.clk(clk), .reset(reset), .ch(ch), .wr_in(wr_in),
                   .level(level), .din(din), .noisy(noisy));
    always #5 clk = ~clk;

    integer errors = 0, checks = 0;

    // ---------------- modelo independiente ----------------
    logic [15:0] m_lfsr;
    logic        m_hit;
    logic [7:0]  m_out;
    always @(posedge clk) begin
        if (reset) m_lfsr <= 16'hACE1;
        else if (ch == 2'd0 && !wr_in)
            m_lfsr <= {m_lfsr[0] ^ m_lfsr[2] ^ m_lfsr[3] ^ m_lfsr[5], m_lfsr[15:1]};
    end
    always @(negedge clk) begin
        #2;                                       // entradas ya estables
        if (!reset) begin
            m_hit = (m_lfsr[7:0] < level * 16);
            m_out = m_hit ? {8{m_lfsr[8]}} : din;
            checks = checks + 1;
            if (noisy !== m_out || dut.lfsr !== m_lfsr) begin
                errors = errors + 1;
                if (errors < 10) $display("ERROR t=%0t: noisy=%h esp=%h lfsr=%h esp=%h",
                                          $time, noisy, m_out, dut.lfsr, m_lfsr);
            end
        end
    end

    integer n, hits, lv, k;
    logic [15:0] seed;
    logic [7:0]  r, g, b;
    initial begin
        repeat (3) @(negedge clk);
        reset = 0;
        @(negedge clk);

        // 1) periodo: con ch = 0 y wr_in = 0 el LFSR avanza cada ciclo
        seed = dut.lfsr; n = 0;
        do begin
            @(negedge clk); n = n + 1;
            if (dut.lfsr == 16'h0000) begin errors = errors + 1; $display("ERROR: LFSR = 0"); end
        end while (dut.lfsr != seed && n < 70000);
        checks = checks + 1;
        if (n != 65535) begin errors = errors + 1; $display("ERROR: periodo %0d", n); end
        else $display("  periodo del LFSR = %0d (maximo 2^16 - 1)", n);

        // 2) aciertos exactos por nivel en un periodo completo
        for (lv = 0; lv < 4; lv = lv + 1) begin
            level = lv[1:0]; hits = 0;
            for (k = 0; k < 65535; k = k + 1) begin
                @(negedge clk);
                if (dut.hit) hits = hits + 1;
            end
            checks = checks + 1;
            if (hits != ((lv == 0) ? 0 : 256*16*lv - 1)) begin
                errors = errors + 1;
                $display("ERROR: nivel %0d -> %0d aciertos", lv, hits);
            end else
                $display("  nivel %0d: %0d aciertos de 65535 (%0.2f %%)", lv, hits, 100.0*hits/65535.0);
        end

        // 3) entradas aleatorias (ch, wr_in, level, din): comparacion ciclo a ciclo
        for (k = 0; k < 200000; k = k + 1) begin
            @(negedge clk);
            ch = $urandom % 3; wr_in = $urandom % 2; level = $urandom % 4; din = $urandom % 256;
        end

        // 4) los 3 bytes de un pixel: misma decision
        level = 2'd3; hits = 0;
        for (k = 0; k < 3000; k = k + 1) begin
            @(negedge clk); ch = 0; wr_in = 0;                     // esperando el byte R
            repeat ($urandom % 50) @(negedge clk);
            r = $urandom % 256; g = $urandom % 256; b = $urandom % 256;
            ch = 0; wr_in = 1; din = r; #1; r = noisy;             // byte R
            @(negedge clk); ch = 1; din = g; #1; g = noisy;        // byte G
            @(negedge clk); ch = 2; din = b; #1; b = noisy;        // byte B
            if (dut.hit) begin
                hits = hits + 1;
                checks = checks + 1;
                if (!((r == 8'h00 && g == 8'h00 && b == 8'h00) || (r == 8'hFF && g == 8'hFF && b == 8'hFF))) begin
                    errors = errors + 1; $display("ERROR: pixel con ruido no uniforme %h %h %h", r, g, b);
                end
            end
            @(negedge clk); ch = 0; wr_in = 0;
        end
        $display("  %0d pixeles con ruido de 3000: todos blancos o negros completos", hits);

        $display("TB tb_noise_gen: %0d verificaciones, %0d errores -> %s",
                 checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
