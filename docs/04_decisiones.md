# Decisiones de diseño (D1–D14)

Cada decisión tiene alternativas descartadas, el motivo y el requisito que cumple.
Fueron propuestas por la IA con sus alternativas y escogidas por el equipo (ver `docs/ia/`).

| ID | Decisión | Alternativas descartadas | Motivo | Requisito |
|---|---|---|---|---|
| D1 | Bordes: **replicar el borde** (se limita la coordenada del vecino a 0..127, M5–M8) | Ceros (marco oscuro y bordes falsos en el Laplaciano) / copiar el original | Sin artefactos; en hardware es bit de signo/comparador + mux | R-P1 |
| D2 | Laplaciano y LoG: **valor absoluto saturado a 255** (M14, M15) | L+128 (poco contraste) / saturar a 0 (se pierde la mitad de los bordes) | Bordes claros sobre fondo negro | R-P1 |
| D3 | Unsharp con **k = 1 fijo**: 2·I − G, saturado 0..255 (M17, M18) | k seleccionable | Definición clásica; desplazamiento, resta y saturación | R-P1 |
| D4 | Ruido **sal y pimienta en la FPGA con LFSR de 16 bits** (M2–M4), densidad con SW[4:3] | Ruido en Python (choca con R-F01) / ruido gaussiano en hardware | Cumple R-P4 y R-F01 a la vez | R-P4, R-F01 |
| D5 | UART 8N1 a 115200: cabecera 0xAA + 49 152 bytes (fila por fila, R-G-B); la FPGA responde 49 152 bytes | Sin cabecera / orden por planos | Una escritura de 24 b por píxel; punto de sincronización | R-P2 |
| D6 | **Timeout de recepción** de ~100 ms (TOUT_CNT 24 b) | Solo botón de reset | Evita bloqueos si se pierde un byte | R-P2, R-G03 |
| D7 | Notación de la guía del profesor en todos los diagramas | — | Es la notación del profesor | R-G06 |
| D8 | **Esquemático RTL único y continuo** (hoja A1) | Figuras por bloque (v1) | Retroalimentación del profesor (28-oct) | R-G06 |
| D9 | **21 multiplexores numerados M1–M21** con ancho, entradas y selección; 37 instancias (M11–M18 ×3) | Mux sin identificar | Retroalimentación del profesor | R-G06 |
| D10 | Motor de convolución **secuencial**: 11 ciclos/píxel, ≈1,8 ms por pasada | Line buffers / 9 lecturas en paralelo | La UART tarda 4,3 s: más velocidad no aporta; más fácil de verificar y explicar | R-P1 |
| D11 | **SystemVerilog con el estilo de las diapositivas 4 y 8**; un archivo por bloque, mismos nombres de señales | Verilog-2001 / `typedef enum` | Idioma de la diapositiva 8; Vivado lo soporta | R-G06 |
| D12 | Salida **rx_en** (estado RECV): borra BYTE_CNT, WR_CNT y TOUT_CNT fuera de RECV | Contar siempre | La cabecera o basura en IDLE se contarían como R del primer píxel | R-P2 |
| D13 | **last_px = pix_valid · (WR_CNT = 16383)**; COL/ROW/TAP_CNT se borran con ¬seq_en | Comparar solo la cuenta | La FSM saldría de RECV antes de guardar el último píxel | R-P2 |
| D14 | Parámetros (LOG_W, CLKS_PER_BIT, TIMEOUT, DEB_BITS) para simular con imagen 8×8 | Simular siempre 128×128 a 868 ciclos/bit | Mismo hardware; la simulación tarda segundos | R-G03 |
