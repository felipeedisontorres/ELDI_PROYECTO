// ============================================================================
// Bloque 1 - uart_rx: receptor UART 8N1 (115200 baudios con reloj de 100 MHz)
// ----------------------------------------------------------------------------
// Hardware (igual al esquematico):
//   RX_BUSY  : 1 FF. Se pone en 1 cuando la linea baja (bit de inicio) y vuelve
//              a 0 al muestrear el bit de parada.
//   BAUD_RX  : contador mod CLKS_PER_BIT (10 b). Borrado mientras RX_BUSY = 0.
//              sample = (BAUD_RX == HALF) marca la MITAD de cada bit.
//   BIT_RX   : contador de muestras (4 b): 0 = inicio, 1..8 = datos, 9 = parada.
//   SR_RX    : registro de desplazamiento de 8 b; entra rx por el MSB en cada
//              muestra (el LSB llega primero). En la muestra 9 ya contiene el
//              byte completo: rx_valid = sample & (BIT_RX == 9).
// Sin sincronizador (decision D15): mientras RX_BUSY = 0 la entrada asincrona
// solo llega al FF RX_BUSY; durante el byte solo se lee a mitad de bit.
// ============================================================================
module uart_rx #(
    parameter int CLKS_PER_BIT = 868            // 100 MHz / 115200 = 868,06
) (
    input  logic       clk,
    input  logic       reset,                   // sincrono, activo en alto
    input  logic       rx,                      // pin UART_TXD_IN (directo)
    output logic       rx_valid,                // pulso de 1 ciclo: byte listo
    output logic [7:0] rx_data                  // byte recibido (valido con rx_valid)
);
    localparam int BW   = $clog2(CLKS_PER_BIT); // 10 bits para 868
    localparam int HALF = CLKS_PER_BIT/2 - 1;   // 433: mitad del bit
    localparam int LAST = CLKS_PER_BIT - 1;     // 867: ultimo ciclo del bit

    logic          rx_busy;
    logic [BW-1:0] baud_rx;
    logic [3:0]    bit_rx;
    logic          sample;

    assign sample   = (baud_rx == HALF[BW-1:0]);   // comparador "= 433"
    assign rx_valid = sample & (bit_rx == 4'd9);   // comparador "= 9" + AND

    // RX_BUSY: MUX 2:1 con selector rx_busy -> 0: ~rx (arranque), 1: ~rx_valid (fin)
    always_ff @(posedge clk) begin
        if (reset)        rx_busy <= 1'b0;
        else if (rx_busy) rx_busy <= ~rx_valid;
        else              rx_busy <= ~rx;
    end

    // BAUD_RX: contador mod CLKS_PER_BIT con borrado (CLR = ~rx_busy)
    always_ff @(posedge clk) begin
        if (reset | ~rx_busy | (baud_rx == LAST[BW-1:0])) baud_rx <= '0;
        else                                              baud_rx <= baud_rx + 1'b1;
    end

    // BIT_RX: contador de muestras (CLR = ~rx_busy, EN = sample)
    always_ff @(posedge clk) begin
        if (reset | ~rx_busy) bit_rx <= '0;
        else if (sample)      bit_rx <= bit_rx + 1'b1;
    end

    // SR_RX: desplazamiento a la derecha en cada muestra (EN = sample, SI = rx)
    always_ff @(posedge clk) begin
        if (reset)       rx_data <= '0;
        else if (sample) rx_data <= {rx, rx_data[7:1]};
    end
endmodule
