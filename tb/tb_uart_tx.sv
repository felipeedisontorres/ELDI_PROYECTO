`timescale 1ns/1ps
module tb_uart_tx;
    localparam int CPB = 868;

    logic       clk = 0, reset = 1, start = 0;
    logic [7:0] data = 0;
    logic       tx, busy;

    uart_tx #(.CLKS_PER_BIT(CPB)) dut (.clk(clk), .reset(reset), .start(start),
                                       .data(data), .tx(tx), .busy(busy));
    always #5 clk = ~clk;

    integer errors = 0, checks = 0;
    integer cyc = 0;
    integer load_cyc = -1;
    logic [9:0] frame = 10'h3FF;
    integer nbytes = 0;
    integer busy_len = 0;

    always @(posedge clk) cyc <= cyc + 1;

    integer rel;
    logic   exp_tx, exp_busy;
    always @(negedge clk) begin
        #1;
        if (!reset) begin
            if (load_cyc < 0) begin exp_tx = 1'b1; exp_busy = 1'b0; end
            else begin
                rel = cyc - load_cyc;
                if (rel < 10*CPB) begin exp_tx = frame[rel / CPB]; exp_busy = 1'b1; end
                else begin exp_tx = 1'b1; exp_busy = 1'b0; end
            end
            checks = checks + 1;
            if (tx !== exp_tx || busy !== exp_busy) begin
                errors = errors + 1;
                if (errors < 10)
                    $display("ERROR t=%0t: tx=%b (esp %b) busy=%b (esp %b)", $time, tx, exp_tx, busy, exp_busy);
            end
        end
    end

    task automatic send(input [7:0] b);
        begin
            @(negedge clk);
            while (busy) @(negedge clk);
            data  = b; start = 1'b1;
            @(negedge clk);
            start = 1'b0;
            load_cyc = cyc;
            frame = {1'b1, b, 1'b0};
            nbytes = nbytes + 1;
        end
    endtask

    integer k;
    initial begin
        repeat (3) @(negedge clk);
        reset = 0;
        repeat (50) @(negedge clk);

        for (k = 0; k < 256; k = k + 1) send(k[7:0]);

        for (k = 0; k < 32; k = k + 1) begin
            send($urandom % 256);
            repeat ($urandom % 2000) @(negedge clk);
        end
        while (busy) @(negedge clk);
        repeat (2*CPB) @(negedge clk);

        send(8'h00);
        busy_len = 0;
        while (busy) begin @(negedge clk); busy_len = busy_len + 1; end
        checks = checks + 1;
        if (busy_len != 10*CPB) begin
            errors = errors + 1;
            $display("ERROR: busy duro %0d ciclos (esperado %0d)", busy_len, 10*CPB);
        end else
            $display("  busy dura %0d ciclos = 10 bits x %0d", busy_len, CPB);

        $display("  %0d bytes transmitidos y comparados ciclo a ciclo", nbytes);
        $display("TB tb_uart_tx: %0d verificaciones, %0d errores -> %s",
                 checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
