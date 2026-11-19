# ============================================================================
# configurar_proyecto.tcl - Proyecto #8 Image Processor (2D filters), v4.1
# ----------------------------------------------------------------------------
# Crea el proyecto de Vivado con el diseno (rtl/), los testbenches (tb/) y los
# pines (constraints/). Uso: abrir Vivado y en la Tcl Console escribir, con
# barras / en la ruta:
#     source C:/ruta/al/repositorio/vivado/configurar_proyecto.tcl
# - Si no hay ningun proyecto abierto, crea uno nuevo en vivado/proyecto/
#   (esa carpeta no se sube a GitHub).
# - Si ya hay un proyecto abierto, le pone la parte correcta y le agrega los
#   archivos.
# Los archivos se agregan por referencia: si se edita rtl/ en el repositorio,
# Vivado usa la version editada.
# ============================================================================

# Tarjeta: "nexys_a7_100t" (Nexys A7-100T y Nexys 4 DDR) o "nexys4_original"
set placa "nexys_a7_100t"
set parte "xc7a100tcsg324-1"

set aqui [file dirname [file normalize [info script]]]
set base [file dirname $aqui]

# 1) Proyecto y FPGA: XC7A100T, encapsulado CSG324, grado de velocidad -1
if {[catch {current_project}]} {
    create_project eldi_p8 $aqui/proyecto -part $parte -force
} else {
    set_property part $parte [current_project]
}

# 2) Diseno (lo que se sintetiza)
add_files -norecurse -fileset sources_1 [lsort [glob $base/rtl/*.sv]]
set_property top image_proc_top [get_filesets sources_1]

# 3) Restricciones: pines y reloj de 100 MHz
add_files -norecurse -fileset constrs_1 $base/constraints/$placa.xdc

# 4) Testbenches (solo simulacion). La simulacion corre hasta el final sola.
add_files -norecurse -fileset sim_1 [lsort [glob $base/tb/*.sv]]
set_property top tb_image_proc_top [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]
set_property -name {xsim.simulate.runtime} -value {all} -objects [get_filesets sim_1]

update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
puts "Listo: parte $parte, top image_proc_top, pines $placa.xdc, simulacion tb_image_proc_top."
