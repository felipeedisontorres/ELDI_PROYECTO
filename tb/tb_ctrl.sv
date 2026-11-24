`timescale 1ns/1ps
module tb_ctrl;
    logic clk = 0, reset = 1, btnc = 0, fin = 0;
    logic [2:0] sw_mode = 0;
    logic [1:0] state, ksel;
    logic [2:0] mode;
    logic idle, absm, src_tmp, tmp_wr;

    ctrl dut (.clk(clk), .reset(reset), .btnc(btnc), .sw_mode(sw_mode), .fin(fin),
              .state(state), .mode(mode), .idle(idle), .ksel(ksel), .absm(absm),
              .src_tmp(src_tmp), .tmp_wr(tmp_wr));
    always #5 clk = ~clk;

    integer errors = 0, checks = 0;

    task automatic expect_out(input [1:0] st, input [2:0] md, input [1:0] ks,
                              input logic ab, input logic st2, input logic tw);
        begin
            #1;
            checks = checks + 1;
            if (state !== st || mode !== md || idle !== (st == 2'b00) ||
                (st != 2'b00 && (ksel !== ks || absm !== ab)) || src_tmp !== st2 || tmp_wr !== tw) begin
                errors = errors + 1;
                $display("ERROR: state=%b mode=%b ksel=%b absm=%b src=%b tw=%b (esp %b %b %b %b %b %b)",
                         state, mode, ksel, absm, src_tmp, tmp_wr, st, md, ks, ab, st2, tw);
            end
        end
    endtask

    function automatic [2:0] p1_dec(input [2:0] md);
        if (md[2])                 p1_dec = {2'b10, 1'b0};
        else case (md[1:0])
            2'b00: p1_dec = {2'b00, 1'b0};
            2'b01: p1_dec = {2'b01, 1'b1};
            2'b10: p1_dec = {2'b00, 1'b0};
            default: p1_dec = {2'b11, 1'b0};
        endcase
    endfunction

    integer m, use_btn, w;
    logic [2:0] d;
    initial begin
        repeat (2) @(negedge clk);
        reset = 0;
        @(negedge clk);
        expect_out(2'b00, 3'b000, 2'b00, 0, 0, 0);
        for (use_btn = 0; use_btn < 2; use_btn = use_btn + 1)
            for (m = 0; m < 8; m = m + 1) begin
                sw_mode = m; @(negedge clk);
                expect_out(2'b00, m[2:0], 2'b00, 0, 0, 0);
                if (use_btn) btnc = 1; else fin = 1;
                @(negedge clk); btnc = 0; fin = 0;
                d = p1_dec(m[2:0]);
                expect_out(2'b01, m[2:0], d[2:1], d[0], 0, (m == 2));
                sw_mode = ~m[2:0]; btnc = 1;
                for (w = 0; w < 5; w = w + 1) begin
                    @(negedge clk);
                    expect_out(2'b01, m[2:0], d[2:1], d[0], 0, (m == 2));
                end
                btnc = 0;
                fin = 1; @(negedge clk); fin = 0;
                if (m == 2) begin
                    expect_out(2'b10, 3'b010, 2'b01, 1, 1, 0);
                    btnc = 1;
                    for (w = 0; w < 5; w = w + 1) begin
                        @(negedge clk);
                        expect_out(2'b10, 3'b010, 2'b01, 1, 1, 0);
                    end
                    btnc = 0;
                    fin = 1; @(negedge clk); fin = 0;
                end
                expect_out(2'b00, m[2:0], 2'b00, 0, 0, 0);
                @(negedge clk);
                expect_out(2'b00, ~m[2:0], 2'b00, 0, 0, 0);
            end
        $display("TB tb_ctrl: %0d verificaciones, %0d errores -> %s",
                 checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
