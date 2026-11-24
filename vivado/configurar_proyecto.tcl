set placa "nexys_a7_100t"
set parte "xc7a100tcsg324-1"

set aqui [file dirname [file normalize [info script]]]
set base [file dirname $aqui]

if {[catch {current_project}]} {
    create_project eldi_p8 $aqui/proyecto -part $parte -force
} else {
    set_property part $parte [current_project]
}

add_files -norecurse -fileset sources_1 [lsort [glob $base/rtl/*.sv]]
set_property top image_proc_top [get_filesets sources_1]

add_files -norecurse -fileset constrs_1 $base/constraints/$placa.xdc

add_files -norecurse -fileset sim_1 [lsort [glob $base/tb/*.sv]]
set_property top tb_image_proc_top [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]
set_property -name {xsim.simulate.runtime} -value {all} -objects [get_filesets sim_1]

update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
puts "Listo: parte $parte, top image_proc_top, pines $placa.xdc, simulacion tb_image_proc_top."
