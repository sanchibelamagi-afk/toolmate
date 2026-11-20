from toolmate.services.scan_service import ScanService


def test_scan_service_loads_sample_manifest():
    entries = ScanService("config/manifest.yaml").scan()

    assert {entry.id for entry in entries} == {"python", "ngspice", "kicad"}
