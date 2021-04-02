import gsflow
import os
import numpy as np
from gsflow import ControlFile, PrmsParameters, PrmsData


ws = os.path.abspath(os.path.dirname(__file__))


def test_load_write_model_prms_only():
    local_ws = os.path.join(ws, "..", "examples", "data", "sagehen", "prms", "windows")
    control_file = "sagehen.control"
    gs = gsflow.GsflowModel.load_from_file(os.path.join(local_ws, control_file))
    assert isinstance(gs.control, ControlFile)
    assert isinstance(gs.prms.parameters, PrmsParameters)
    assert isinstance(gs.prms.data, PrmsData)

    ws2 = os.path.join(ws, "temp")
    gs.write_input(workspace=ws2)

    gs2 = gsflow.GsflowModel.load_from_file(os.path.join(ws2, control_file))

    assert len(gs2.control.record_names) == len(gs.control.record_names)
    assert len(gs2.prms.parameters.record_names) == len(gs.prms.parameters.record_names)


def test_load_write_gsflow_modflow():
    local_ws = os.path.join(ws, "..", "examples", "data", "sagehen", "modflow")
    nam = "saghen.nam"
    ml = gsflow.modflow.Modflow.load(nam, model_ws=local_ws)
    assert isinstance(ml, gsflow.modflow.Modflow)

    ws2 = os.path.join(ws, "temp")
    ml.change_model_ws(ws2)
    ml.write_input()

    ml2 = gsflow.modflow.Modflow.load(nam, model_ws=ws2)

    assert len(ml.packagelist) == len(ml2.packagelist)
    assert ml.nrow_ncol_nlay_nper == ml2.nrow_ncol_nlay_nper


def test_load_write_gsflow():

    local_ws = os.path.join(ws, "..", "examples", "data", "sagehen", "gsflow")
    control_file = "saghen_new_cont.control"

    gs = gsflow.GsflowModel.load_from_file(os.path.join(local_ws, control_file))
    assert isinstance(gs.control, ControlFile)
    assert isinstance(gs.prms.parameters, PrmsParameters)
    assert isinstance(gs.prms.data, PrmsData)
    assert isinstance(gs.mf, gsflow.modflow.Modflow)

    ws2 = os.path.join(ws, "temp")

    # change ws only ...
    gs.write_input(workspace=ws2)

    gs2 = gsflow.GsflowModel.load_from_file(os.path.join(ws2, control_file))
    assert len(gs2.control.record_names) == len(gs.control.record_names)
    assert len(gs2.prms.parameters.record_names) == len(gs.prms.parameters.record_names)
    assert len(gs2.mf.packagelist) == len(gs.mf.packagelist)
    assert gs2.mf.nrow_ncol_nlay_nper == gs.mf.nrow_ncol_nlay_nper

    local_ws = os.path.join(ws, "..", "examples", "data", "sagehen", "gsflow")
    control_file = "saghen_new_cont.control"

    gs = gsflow.GsflowModel.load_from_file(os.path.join(local_ws, control_file))
    assert not gs.modflow_only
    assert not gs.prms_only

    ws2 = os.path.join(ws, "temp")
    basename = "test2"

    # change ws and basename...
    gs.write_input(basename=basename, workspace=ws2)

    gs2 = gsflow.GsflowModel.load_from_file(os.path.join(ws2, "test2_cont.control"))
    assert len(gs2.control.record_names) == len(gs.control.record_names)
    assert len(gs2.prms.parameters.record_names) == len(gs.prms.parameters.record_names)
    assert len(gs2.mf.packagelist) == len(gs.mf.packagelist)
    assert gs2.mf.nrow_ncol_nlay_nper == gs.mf.nrow_ncol_nlay_nper


    # change basename only
    basename = "test3"
    gs.write_input(basename="test3")

    gs3 = gsflow.GsflowModel.load_from_file(os.path.join(ws2, "test3_cont.control"))
    assert len(gs3.control.record_names) == len(gs.control.record_names)
    assert len(gs3.prms.parameters.record_names) == len(gs.prms.parameters.record_names)
    assert len(gs3.mf.packagelist) == len(gs.mf.packagelist)
    assert gs3.mf.nrow_ncol_nlay_nper == gs.mf.nrow_ncol_nlay_nper

    # no basename, no workspace
    gs.write_input()

    gs4 = gsflow.GsflowModel.load_from_file(os.path.join(ws2, "test3_cont.control"))
    assert len(gs4.control.record_names) == len(gs.control.record_names)
    assert len(gs4.prms.parameters.record_names) == len(gs.prms.parameters.record_names)
    assert len(gs4.mf.packagelist) == len(gs.mf.packagelist)
    assert gs4.mf.nrow_ncol_nlay_nper == gs.mf.nrow_ncol_nlay_nper


if __name__ == "__main__":
    test_load_write_model_prms_only()
    test_load_write_gsflow_modflow()
    test_load_write_gsflow()
