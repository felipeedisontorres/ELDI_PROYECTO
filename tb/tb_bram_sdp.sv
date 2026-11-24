`timescale 1ns/1ps
module tb_bram_sdp;
    localparam int AW = 16;
    logic clk = 0, we = 0;
    logic [AW-1:0] waddr = 0, raddr = 0;
    logic [7:0] din = 0, dout;

    bram_sdp #(.AW(AW), .DW(8)) dut (.clk(clk), .we(we), .waddr(waddr), .din(din),
                                     .raddr(raddr), .dout(dout));
    always #5 clk = ~clk;

    integer errors = 0, checks = 0;
    logic [7:0] model [0:(1<<AW)-1];
    logic [7:0] exp_next;
    logic       chk_next = 0;
    integer i, k;

    always @(posedge clk) begin
        if (chk_next) begin
            checks = checks + 1;
            #1;
            if (dout !== exp_next) begin
                errors = errors + 1;
                if (errors < 10) $display("ERROR: dout=%h esperado %h", dout, exp_next);
            end
        end
    end

    task automatic cycle(input logic w, input [AW-1:0] wa, input [7:0] d, input [AW-1:0] ra);
        begin
            @(negedge clk);
            we = w; waddr = wa; din = d; raddr = ra;
            exp_next = model[ra];
            chk_next = 1;
            @(posedge clk); #0;
            if (w) model[wa] = d;
        end
    endtask

    initial begin
        for (i = 0; i < (1<<AW); i = i + 1) model[i] = 8'h00;
        cycle(0, 0, 0, 16'h0000);
        cycle(0, 0, 0, 16'hFFFF);
        cycle(1, 16'h0000, 8'h11, 16'h1234);
        cycle(1, 16'hFFFF, 8'hEE, 16'h0000);
        cycle(0, 0, 0, 16'hFFFF);
        cycle(1, 16'h0ABC, 8'h5A, 16'h0001);
        cycle(0, 0, 0, 16'h0ABC);
        cycle(1, 16'h0ABC, 8'hA5, 16'h0ABC);
        cycle(0, 0, 0, 16'h0ABC);
        for (k = 0; k < 300000; k = k + 1)
            cycle($urandom % 2, $urandom % (1<<AW), $urandom % 256, $urandom % (1<<AW));
        for (k = 0; k < (1<<AW); k = k + 1) cycle(1, k[AW-1:0], k[7:0] ^ k[15:8], (k + 7) % (1<<AW));
        for (k = 0; k < (1<<AW); k = k + 1) cycle(0, 0, 0, k[AW-1:0]);
        @(negedge clk); chk_next = 0;
        repeat (2) @(negedge clk);
        $display("TB tb_bram_sdp: %0d verificaciones, %0d errores -> %s",
                 checks, errors, (errors == 0) ? "PASS" : "FAIL");
        $finish;
    end
endmodule
