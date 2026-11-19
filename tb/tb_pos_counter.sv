// ============================================================================
// tb_pos_counter: testbench autoverificable del contador de posicion (bloque 3)
// Instancias con LOG_W = 7 (128 x 128) y LOG_W = 3 (8 x 8). Enable aleatorio.
// Casos: secuencia R,G,B -> columna -> fila; fin solo al avanzar desde (2, W-1, W-1);
// vuelta a (0,0,0); en = 0 congela; dos barridos completos.
// ============================================================================
`timescale 1ns/1ps
module tb_pos_counter;
    logic clk = 0, reset = 1, en = 0;
    logic [1:0] ch7, ch3;
    logic [6:0] col7, row7;
    logic [2:0] col3, row3;
    logic fin7, fin3;

    pos_counter #(.LOG_W(7)) d7 (.clk(clk), .reset(reset), .en(en),
                                 .ch(ch7), .col(col7), .row(row7), .fin(fin7));
    pos_counter #(.LOG_W(3)) d3 (.clk(clk), .reset(reset), .en(en),
                                 .ch(ch3), .col(col3), .row(row3), .fin(fin3));
    always #5 clk = ~clk;

    integer errors = 0, checks = 0;
    integer m7 = 0, m3 = 0;                      // modelo: indice lineal del byte
    integer nlast7 = 0, nlast3 = 0;

    always @(negedge clk) begin
        #1;                                       // en ya cambio en este flanco
        if (!reset) begin
            checks = checks + 2;
            if (row7 !== m7 / 384 || col7 !== (m7 / 3) % 128 || ch7 !== m7 % 3 ||
                fin7 !== (en && m7 == 49151)) begin
                errors = errors + 1;
                if (errors < 10) $display("ERROR W=128: m=%0d -> row=%0d col=%0d ch=%0d fin=%b",
                                          m7, row7, col7, ch7, fin7);
            end
            if (row3 !== m3 / 24 || col3 !== (m3 / 3) % 8 || ch3 !== m3 % 3 ||
                fin3 !== (en && m3 == 191)) begin
                errors = errors + 1;
                if (errors < 10) $display("ERROR W=8: m=%0d -> row=%0d col=%0d ch=%0d fin=%b",
                                          m3, row3, col3, ch3, fin3);
            end
        end
    end
    always @(posedge clk) begin
        if (!reset && en) begin
            if (fin7) nlast7 = nlast7 + 1;
            if (fin3) nlast3 = nlast3 + 1;
            m7 = (m7 + 1) % 49152;
            m3 = (m3 + 1) % 192;
        end
    end

    integer k;
    initial begin
        repeat (3) @(negedge clk);
        reset = 0;
        for (k = 0; k < 2*49152*2 + 37; k = k + 1) begin
            @(negedge clk);
            en = ($urandom % 4) != 0;            // 75 % de los ciclos
        end
        @(negedge clk); en = 0;
        repeat (3) @(negedge clk);
        $display("  W=128: fin visto %0d veces; W=8: %0d veces", nlast7, nlast3);
        $display("TB tb_pos_counter: %0d verificaciones, %0d errores -> %s",
                 checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
