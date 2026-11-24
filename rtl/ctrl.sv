module ctrl (
    input  logic       clk,
    input  logic       reset,
    input  logic       btnc,
    input  logic [2:0] sw_mode,
    input  logic       fin,
    output logic [1:0] state,
    output logic [2:0] mode,
    output logic       idle,
    output logic [1:0] ksel,
    output logic       absm,
    output logic       src_tmp,
    output logic       tmp_wr
);
    localparam logic [1:0] IDLE = 2'b00;
    localparam logic [1:0] P1   = 2'b01;
    localparam logic [1:0] P2   = 2'b10;

    logic [1:0] next;
    logic       two_pass;

    always_ff @(posedge clk) begin
        if (reset)     mode <= 3'b000;
        else if (idle) mode <= sw_mode;
    end

    (* fsm_encoding = "none" *)
    logic [1:0] state_q;
    always_ff @(posedge clk) begin
        if (reset) state_q <= IDLE;
        else       state_q <= next;
    end
    assign state = state_q;

    always_comb begin
        case (state_q)
            IDLE:    next = (fin | btnc) ? P1 : IDLE;
            P1:      next = fin ? (two_pass ? P2 : IDLE) : P1;
            P2:      next = fin ? IDLE : P2;
            default: next = IDLE;
        endcase
    end

    assign idle     = (state_q == IDLE);
    assign two_pass = (mode == 3'b010);
    assign src_tmp  = (state_q == P2);
    assign tmp_wr   = (state_q == P1) & two_pass;

    assign ksel = (state_q == P2)       ? 2'b01 :
                  mode[2]               ? 2'b10 :
                  (mode[1:0] == 2'b11)  ? 2'b11 :
                  (mode[1:0] == 2'b01)  ? 2'b01 :
                                          2'b00;
    assign absm = (ksel == 2'b01);
endmodule
