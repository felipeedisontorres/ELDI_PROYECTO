// ============================================================================
// tb_post_proc: testbench autoverificable del post-procesamiento (bloque 7)
// EXHAUSTIVO: los 32 768 valores posibles del ACC (15 b con signo) con absm = 0
// y absm = 1 (65 536 casos). Referencia: s = floor(acc/16); si s < 0 ->
// (absm ? -s : 0); luego min(., 255).
// ============================================================================
`timescale 1ns/1ps
module tb_post_proc;
    logic signed [14:0] acc = 0;
    logic absm = 0;
    logic [7:0] y;

    post_proc dut (.acc(acc), .absm(absm), .y(y));

    integer errors = 0, checks = 0;
    integer a, m, s, e;
    initial begin
        for (m = 0; m < 2; m = m + 1)
            for (a = -16384; a <= 16383; a = a + 1) begin
                acc = a; absm = m; #1;
                s = (a >= 0) ? a / 16 : -((-a + 15) / 16);   // floor(a/16)
                if (s < 0) e = m ? -s : 0; else e = s;
                if (e > 255) e = 255;
                checks = checks + 1;
                if (y !== e[7:0]) begin
                    errors = errors + 1;
                    if (errors < 10) $display("ERROR: acc=%0d absm=%0d -> y=%0d esperado %0d", a, m, y, e);
                end
            end
        $display("TB tb_post_proc: %0d verificaciones, %0d errores -> %s",
                 checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
