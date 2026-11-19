// ============================================================================
// tb_conv_mac: testbench autoverificable del MAC (bloque 6)
// Para los 4 kernels: vecindarios aleatorios y extremos (todo 0, todo 255,
// centro 255 / vecinos 0, centro 0 / vecinos 255, damero). Comprueba la suma
// en el tap 11 contra una tabla de pesos escrita aparte, que el ACC se
// mantiene en el tap 11 aunque cambie pix, los extremos
// del rango (+-16 320 en el Laplaciano) y que tap = 0 lo borra.
// ============================================================================
`timescale 1ns/1ps
module tb_conv_mac;
    logic clk = 0, reset = 1;
    logic [1:0] ksel = 0;
    logic [3:0] tap = 0;
    logic [7:0] pix = 0;
    logic signed [14:0] acc;

    conv_mac dut (.clk(clk), .reset(reset), .ksel(ksel), .tap(tap),
                  .pix(pix), .acc(acc));
    always #5 clk = ~clk;

    integer errors = 0, checks = 0;
    integer K [0:3][0:8];
    integer nb [0:8];
    integer minacc = 0, maxacc = 0;

    task automatic run(input integer k);
        integer t, ref_sum, i;
        begin
            ref_sum = 0;
            for (i = 0; i < 9; i = i + 1) ref_sum = ref_sum + K[k][i] * nb[i];
            @(negedge clk); ksel = k; tap = 11; pix = $urandom % 256;   // valor viejo en el ACC
            for (t = 0; t <= 10; t = t + 1) begin
                tap = t;
                pix = (t >= 1 && t <= 9) ? nb[t-1] : ($urandom % 256);   // basura en 0 y 10
                @(negedge clk);
            end
            // en el tap 11 (ya acumulado el producto del tap 10) el ACC tiene la suma completa
            repeat (3) begin
                tap = 11; pix = $urandom % 256;
                checks = checks + 1;
                if (acc !== ref_sum) begin
                    errors = errors + 1;
                    if (errors < 10) $display("ERROR k=%0d: acc=%0d esperado %0d", k, acc, ref_sum);
                end
                @(negedge clk);
            end
            if (ref_sum < minacc) minacc = ref_sum;
            if (ref_sum > maxacc) maxacc = ref_sum;
        end
    endtask

    integer k, n, i;
    initial begin
        // tablas de pesos (orden de barrido: fila -1, 0, +1)
        for (i = 0; i < 9; i = i + 1) begin K[0][i] = 0; K[1][i] = 0; K[2][i] = 0; K[3][i] = 0; end
        K[0][0]=1;  K[0][1]=2;  K[0][2]=1;  K[0][3]=2;  K[0][4]=4;   K[0][5]=2;  K[0][6]=1;  K[0][7]=2;  K[0][8]=1;
        K[1][1]=16; K[1][3]=16; K[1][4]=-64; K[1][5]=16; K[1][7]=16;
        K[2][4]=16;
        K[3][0]=-1; K[3][1]=-2; K[3][2]=-1; K[3][3]=-2; K[3][4]=28;  K[3][5]=-2; K[3][6]=-1; K[3][7]=-2; K[3][8]=-1;

        repeat (2) @(negedge clk);
        reset = 0;
        for (k = 0; k < 4; k = k + 1) begin
            for (i = 0; i < 9; i = i + 1) nb[i] = 0;               run(k);
            for (i = 0; i < 9; i = i + 1) nb[i] = 255;             run(k);
            for (i = 0; i < 9; i = i + 1) nb[i] = (i == 4) ? 255 : 0;   run(k);
            for (i = 0; i < 9; i = i + 1) nb[i] = (i == 4) ? 0 : 255;   run(k);
            for (i = 0; i < 9; i = i + 1) nb[i] = (i % 2) ? 255 : 0;    run(k);
            for (i = 0; i < 9; i = i + 1) nb[i] = (i % 2) ? 0 : 255;    run(k);
            for (n = 0; n < 3000; n = n + 1) begin
                for (i = 0; i < 9; i = i + 1) nb[i] = $urandom % 256;
                run(k);
            end
        end
        // tap = 0 borra el ACC (aunque pix tenga cualquier valor)
        @(negedge clk); tap = 0; pix = 8'hFF; @(negedge clk);
        checks = checks + 1;
        if (acc !== 0) begin errors = errors + 1; $display("ERROR: tap = 0 no borra el ACC"); end
        $display("  rango observado del ACC: %0d .. %0d (cabe en 15 b con signo)", minacc, maxacc);
        $display("TB tb_conv_mac: %0d verificaciones, %0d errores -> %s",
                 checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
