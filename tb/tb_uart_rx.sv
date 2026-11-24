`timescale 1ns/1ps
module tb_uart_rx;
    localparam int CPB = 868;

    logic       clk = 0, reset = 1, rx = 1;
    logic       rx_valid;
    logic [7:0] rx_data;

    uart_rx #(.CLKS_PER_BIT(CPB)) dut (.clk(clk), .reset(reset), .rx(rx),
                                       .rx_valid(rx_valid), .rx_data(rx_data));
    always #5 clk = ~clk;

    integer errors = 0, checks = 0;
    logic [7:0] expq [0:1023];
    integer wr_i = 0, rd_i = 0;
    integer cyc = 0, t_start = 0;
    logic   prev_valid = 0;
    logic   ignore = 0;
    integer garbage = 0;

    always @(posedge clk) cyc <= cyc + 1;

    always @(posedge clk) begin
        if (rx_valid && ignore) garbage = garbage + 1;
        else if (rx_valid) begin
            checks = checks + 1;
            if (rd_i >= wr_i) begin
                errors = errors + 1;
                $display("ERROR: rx_valid sin byte enviado (t=%0t)", $time);
            end else begin
                if (rx_data !== expq[rd_i]) begin
                    errors = errors + 1;
                    $display("ERROR: byte %0d recibido %h, esperado %h", rd_i, rx_data, expq[rd_i]);
                end
                rd_i = rd_i + 1;
            end
            if (prev_valid) begin
                errors = errors + 1;
                $display("ERROR: rx_valid dura mas de 1 ciclo");
            end
        end
        prev_valid <= rx_valid;
    end

    task automatic send_byte(input [7:0] b, input integer per, input logic expect_it);
        integer i;
        begin
            if (expect_it) begin expq[wr_i] = b; wr_i = wr_i + 1; end
            @(negedge clk); rx = 1'b0; t_start = cyc;
            repeat (per) @(negedge clk);
            for (i = 0; i < 8; i = i + 1) begin
                rx = b[i];
                repeat (per) @(negedge clk);
            end
            rx = 1'b1;
            repeat (per) @(negedge clk);
        end
    endtask

    integer k, lat;
    initial begin
        repeat (5) @(negedge clk);
        reset = 0;
        repeat (100) @(negedge clk);

        for (k = 0; k < 256; k = k + 1) send_byte(k[7:0], CPB, 1'b1);
        repeat (2*CPB) @(negedge clk);
        checks = checks + 1;
        if (rd_i != 256) begin errors = errors + 1; $display("ERROR: llegaron %0d de 256", rd_i); end
        $display("  caso 1 (256 valores seguidos): %0d recibidos", rd_i);

        for (k = 0; k < 64; k = k + 1) begin
            send_byte($urandom % 256, CPB, 1'b1);
            repeat ($urandom % 3000) @(negedge clk);
        end
        $display("  caso 2 (pausas aleatorias): total %0d", rd_i);

        for (k = 0; k < 32; k = k + 1) send_byte($urandom % 256, (CPB*103)/100, 1'b1);
        for (k = 0; k < 32; k = k + 1) send_byte($urandom % 256, (CPB*97)/100, 1'b1);
        repeat (2*CPB) @(negedge clk);
        $display("  caso 3 (+-3 %% de baudios): total %0d", rd_i);

        fork
            send_byte(8'hA5, CPB, 1'b1);
            begin
                @(posedge rx_valid);
                lat = cyc - t_start;
                checks = checks + 1;
                if (lat < (19*CPB)/2 - 3 || lat > (19*CPB)/2 + 3) begin
                    errors = errors + 1;
                    $display("ERROR: latencia %0d ciclos (esperado ~%0d)", lat, (19*CPB)/2);
                end else
                    $display("  caso 4: rx_valid a %0d ciclos del flanco (9,5 bits = %0d)", lat, (19*CPB)/2);
            end
        join

        k = rd_i;
        repeat (20*CPB) @(negedge clk);
        checks = checks + 1;
        if (rd_i != k) begin errors = errors + 1; $display("ERROR: byte falso en reposo"); end

        ignore = 1;
        fork
            send_byte(8'h3C, CPB, 1'b0);
            begin repeat (4*CPB) @(negedge clk); reset = 1; @(negedge clk); reset = 0; end
        join
        repeat (12*CPB) @(negedge clk);
        ignore = 0;
        k = wr_i;
        for (k = 0; k < 8; k = k + 1) send_byte($urandom % 256, CPB, 1'b1);
        repeat (2*CPB) @(negedge clk);
        checks = checks + 1;
        if (rd_i != wr_i) begin errors = errors + 1; $display("ERROR: tras el reset llegaron %0d de %0d", rd_i, wr_i); end
        $display("  caso 6 (reset a mitad de byte): %0d byte(s) basura durante el reset; luego %0d de %0d correctos",
                 garbage, rd_i, wr_i);

        $display("TB tb_uart_rx: %0d verificaciones, %0d errores -> %s",
                 checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
