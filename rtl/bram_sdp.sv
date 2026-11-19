// ============================================================================
// Bloque 4 - bram_sdp: memoria de doble puerto simple (1 escritura + 1 lectura)
// ----------------------------------------------------------------------------
// Se usa dos veces: BRAM_IN (imagen recibida, con ruido) y BRAM_TMP (resultado
// del Gaussiano en la 1a pasada del LoG). Palabra de 8 b (un canal de color).
// Direccion de 16 b = {fila[6:0], columna[6:0], canal[1:0]} -> 65 536 posiciones
// (las de canal = 3 no se usan). Lectura SINCRONA: el dato sale 1 ciclo despues
// de presentar la direccion (asi Vivado la infiere como Block RAM).
// ============================================================================
module bram_sdp #(
    parameter int AW = 16,
    parameter int DW = 8
) (
    input  logic          clk,
    input  logic          we,
    input  logic [AW-1:0] waddr,
    input  logic [DW-1:0] din,
    input  logic [AW-1:0] raddr,
    output logic [DW-1:0] dout
);
    logic [DW-1:0] mem [0:(1<<AW)-1];

    // Contenido inicial en 0 (valor de encendido de la BRAM; evita X en simulacion).
    // Vivado y Yosys definen SYNTHESIS al sintetizar, asi que este lazo solo se usa
    // en simulacion.
`ifndef SYNTHESIS
    initial begin
        for (int i = 0; i < (1<<AW); i++) mem[i] = '0;
    end
`endif

    always_ff @(posedge clk) begin
        if (we) mem[waddr] <= din;
        dout <= mem[raddr];
    end
endmodule
