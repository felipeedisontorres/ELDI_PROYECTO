`timescale 1ns/1ps
module tb_tap_seq;
    localparam int LOG_W = 7;
    localparam int W = 1 << LOG_W;

    logic clk = 0, reset = 1, go = 1, idle = 0;
    logic [1:0] ch = 0;
    logic [LOG_W-1:0] col = 0, row = 0;
    logic [3:0] tap;
    logic at11;
    logic [2*LOG_W+1:0] naddr;

    tap_seq #(.LOG_W(LOG_W)) dut (.clk(clk), .reset(reset), .go(go), .idle(idle), .ch(ch),
                                  .col(col), .row(row), .tap(tap), .at11(at11), .naddr(naddr));
    always #5 clk = ~clk;

    integer errors = 0, checks = 0;

    function automatic integer clampi(input integer v);
        clampi = (v < 0) ? 0 : (v > W-1) ? W-1 : v;
    endfunction

    integer edr, edc, er, ec;
    task automatic check_addr(input integer t);
        begin
            if (t <= 8) begin edr = t / 3 - 1; edc = t % 3 - 1; end
            else begin edr = 0; edc = 0; end
            er = clampi(row + edr); ec = clampi(col + edc);
            checks = checks + 1;
            if (naddr !== {er[LOG_W-1:0], ec[LOG_W-1:0], ch} || at11 !== (t == 11) || tap !== t[3:0]) begin
                errors = errors + 1;
                if (errors < 10) $display("ERROR: fila=%0d col=%0d tap=%0d -> naddr=%h (esp fila %0d col %0d)",
                                          row, col, tap, naddr, er, ec);
            end
        end
    endtask

    integer r, c, t, hold;
    initial begin
        repeat (2) @(negedge clk);
        reset = 0;
        @(negedge clk);
        for (r = 0; r < W; r = r + 1)
            for (c = 0; c < W; c = c + 1) begin
                row = r; col = c; ch = $urandom % 3;
                go = 1; @(negedge clk);
                go = 0;
                for (t = 0; t <= 11; t = t + 1) begin
                    #1 check_addr(t);
                    @(negedge clk);
                end
                hold = $urandom % 4;
                repeat (hold) begin #1 check_addr(11); @(negedge clk); end
            end
        go = 1; @(negedge clk); go = 0;
        repeat (5) @(negedge clk);
        go = 1; @(negedge clk); go = 0; #1;
        checks = checks + 1;
        if (tap !== 4'd0) begin errors = errors + 1; $display("ERROR: go no borra TAP"); end
        idle = 1;
        repeat (20) @(negedge clk);
        #1 checks = checks + 1;
        if (tap !== 4'd0) begin errors = errors + 1; $display("ERROR: TAP cuenta en IDLE"); end
        idle = 0;
        repeat (3) @(negedge clk);
        #1 checks = checks + 1;
        if (tap !== 4'd3) begin errors = errors + 1; $display("ERROR: TAP no arranca al salir de IDLE"); end
        $display("TB tb_tap_seq: %0d verificaciones, %0d errores -> %s",
                 checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
