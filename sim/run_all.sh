#!/usr/bin/env bash
# ============================================================================
# Corre TODOS los testbenches con Icarus Verilog (iverilog -g2012) y resume.
# Uso (desde la carpeta del proyecto):   bash sim/run_all.sh
# Requiere: iverilog >= 11. En Ubuntu: sudo apt install iverilog gtkwave
# ============================================================================
set -u
cd "$(dirname "$0")/.."
mkdir -p sim/build
RTL="rtl/uart_rx.sv rtl/noise_gen.sv rtl/pos_counter.sv rtl/bram_sdp.sv rtl/tap_seq.sv \
     rtl/conv_mac.sv rtl/post_proc.sv rtl/uart_tx.sv rtl/ctrl.sv rtl/image_proc_top.sv"
TBS="tb_uart_rx tb_uart_tx tb_noise_gen tb_pos_counter tb_bram_sdp tb_tap_seq \
     tb_conv_mac tb_post_proc tb_ctrl tb_image_proc_top"
fails=0
for tb in $TBS; do
    printf '%-22s ' "$tb"
    if ! iverilog -g2012 -o sim/build/$tb.vvp -s $tb $RTL tb/$tb.sv 2> sim/build/$tb.err; then
        echo "ERROR DE COMPILACION (ver sim/build/$tb.err)"; fails=$((fails+1)); continue
    fi
    ( cd sim/build && vvp -n $tb.vvp > $tb.log 2>&1 )
    res=$(grep -E "^TB " sim/build/$tb.log | tail -1)
    echo "${res:-SIN RESULTADO (ver sim/build/$tb.log)}"
    echo "$res" | grep -q "PASS" || fails=$((fails+1))
done
echo "--------------------------------------------------------------"
if [ $fails -eq 0 ]; then echo "TODOS LOS TESTBENCHES: PASS"; else echo "FALLARON: $fails"; fi
exit $fails
