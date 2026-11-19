// tb_wave: testbench solo para generar las formas de onda del informe (imagen 4 x 4, CPB = 8).
// Uso: ver sim/wave/plot_wave.py
`timescale 1ns/1ps
module tb_wave;
    localparam int LOG_W = 2, CPB = 8, W = 4, NB = W*W*3;
    logic CLK100MHZ = 0, CPU_RESETN = 0, UART_TXD_IN = 1, BTNC = 0;
    logic [4:0] SW = 5'b00_000;               // Gaussiano, sin ruido
    logic UART_RXD_OUT; logic [7:0] LED;
    image_proc_top #(.CLKS_PER_BIT(CPB), .LOG_W(LOG_W)) dut (
        .CLK100MHZ(CLK100MHZ), .CPU_RESETN(CPU_RESETN), .UART_TXD_IN(UART_TXD_IN),
        .UART_RXD_OUT(UART_RXD_OUT), .SW(SW), .BTNC(BTNC), .LED(LED));
    always #5 CLK100MHZ = ~CLK100MHZ;
    task automatic send_byte(input [7:0] b);
        integer i;
        begin
            @(negedge CLK100MHZ); UART_TXD_IN = 1'b0; repeat (CPB) @(negedge CLK100MHZ);
            for (i = 0; i < 8; i = i + 1) begin UART_TXD_IN = b[i]; repeat (CPB) @(negedge CLK100MHZ); end
            UART_TXD_IN = 1'b1; repeat (CPB) @(negedge CLK100MHZ);
        end
    endtask
    integer i;
    initial begin
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_wave);
        repeat (4) @(negedge CLK100MHZ); CPU_RESETN = 1;
        repeat (10) @(negedge CLK100MHZ);
        for (i = 0; i < NB; i = i + 1) send_byte((i * 53 + 17) & 8'hFF);
        repeat (400) @(negedge CLK100MHZ);
        $finish;
    end
endmodule
