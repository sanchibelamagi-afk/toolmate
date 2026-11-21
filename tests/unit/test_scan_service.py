from toolmate.services.scan_service import ScanService


def test_scan_service_loads_sample_manifest():
    entries = ScanService("config/manifest.yaml").scan()

    assert {entry.id for entry in entries} == {
        "python",
        "ngspice",
        "kicad",
        "git",
        "ghdl",
        "openmodelica",
        "verilator",
        "iverilog",
        "makerchip",
        "openroad_flow",
        "skywater_sky130_pdk",
        "ihp_pdk",
    }
