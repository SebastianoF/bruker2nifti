import os
import sys

from bruker2nifti._metadata import BrukerMetadata
from bruker2nifti._utils import bruker_read_files

if sys.version_info >= (3, 3):
    import unittest.mock as mock
else:
    import mock as mock


here = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.dirname(here)
banana_data = os.path.join(root_dir, "test_data", "bru_banana")


class TestMetadata(object):
    def test_instantiation(self):
        paths = [
            None,
            "/",
            os.path.join("path", "to", "study"),
            os.path.join("path", "to", "study", "0"),
            os.path.join("path", "to", "study", "1"),
        ]
        for path in paths:
            m = BrukerMetadata(path)
            assert isinstance(m, BrukerMetadata)
            assert m.pfo_input == path

    def test_list_subdirs(self):
        m = BrukerMetadata(banana_data)
        assert m._list_subdirs(banana_data) == ["1", "2", "3"]
        assert m._list_subdirs(os.path.join(banana_data, "1")) == []
        assert m._list_subdirs(os.path.join(banana_data, "1", "pdata")) == ["1"]
        assert m._list_subdirs(os.path.join(banana_data, "1", "pdata", "1")) == []

    def test_list_scans(self):
        data_dir = os.path.join("path", "to", "study")
        expected_scans = ["1", "2", "3", "4"]
        with mock.patch.object(
            BrukerMetadata, "_list_subdirs", return_value=expected_scans
        ) as mock_method:
            m = BrukerMetadata(data_dir)
            scans = m.list_scans()
            mock_method.assert_called_once_with(data_dir)
            assert scans == expected_scans

    def test_list_reconstructions(self):
        data_dir = os.path.join("path", "to", "study")
        selected_scan = "2"
        expected_recons = ["1"]
        expected_dir = os.path.join(data_dir, selected_scan, "pdata")
        with mock.patch.object(
            BrukerMetadata, "_list_subdirs", return_value=expected_recons
        ) as mock_method:
            m = BrukerMetadata(data_dir)
            recons = m.list_recons(selected_scan)
            mock_method.assert_called_once_with(expected_dir)
            assert recons == expected_recons

    # TODO: The following test case is not properly tested yet as the
    #       banana dataset does not include a subject. Will need to add a new
    #       test dataset or update banana to include a subject
    def test_read_subject(self):
        expected_contents = bruker_read_files("subject", banana_data)
        with mock.patch("bruker2nifti._utils.bruker_read_files") as mock_function:
            mock_function.configure_mock(side_effect=bruker_read_files)
            m = BrukerMetadata(banana_data)
            subject = m.read_subject()
            assert subject == expected_contents
            mock_function.assert_called_once_with("subject", banana_data)

    def test_read_recon(self):
        selected_scan = "3"
        selected_recon = "1"
        data_path = os.path.join(banana_data, selected_scan)
        ex_reco = bruker_read_files("reco", data_path, selected_recon)
        ex_visu_pars = bruker_read_files("visu_pars", data_path, selected_recon)
        expected_contents = {"reco": ex_reco, "visu_pars": ex_visu_pars}
        with mock.patch("bruker2nifti._utils.bruker_read_files") as mock_function:
            mock_function.configure_mock(side_effect=bruker_read_files)
            m = BrukerMetadata(banana_data)
            recon = m.read_recon(selected_scan, selected_recon)
            assert recon.keys() == expected_contents.keys()
            assert recon["reco"].keys() == ex_reco.keys()
            assert recon["visu_pars"].keys() == ex_visu_pars.keys()
            mock_function.assert_called()

    def test_read_recons(self):
        selected_scan = "2"
        root_path = os.path.join("path", "to")
        data_path = os.path.join(root_path, selected_scan)
        expected_keys = ["1", "2"]
        with mock.patch.object(
            BrukerMetadata, "list_recons", return_value=["1", "2"]
        ) as mock_list_recons, mock.patch.object(
            BrukerMetadata, "read_recon", return_value=None
        ) as mock_read_recon:
            m = BrukerMetadata(root_path)
            recons = m.read_recons(selected_scan)
            assert list(recons.keys()) == expected_keys
            mock_list_recons.assert_called_once()
            mock_read_recon.assert_called()

    def test_read_scan(self):
        selected_scan = "1"
        data_path = os.path.join(banana_data, selected_scan)
        expected_keys = ["acqp", "method", "recons"]
        ex_acqp = bruker_read_files("acqp", data_path)
        ex_method = bruker_read_files("method", data_path)
        with mock.patch.object(
            BrukerMetadata, "read_recons", return_value={"1": None, "2": None}
        ) as mock_read_recons:
            m = BrukerMetadata(banana_data)
            scan = m.read_scan(selected_scan)
            assert set(scan.keys()) == set(expected_keys)
            assert scan["acqp"].keys() == ex_acqp.keys()
            assert scan["method"].keys() == ex_method.keys()
            assert set(scan["recons"].keys()) == {"1", "2"}
            mock_read_recons.assert_called_once_with(selected_scan)

    def test_read_scans(self):
        expected_keys = ["1", "2", "3", "4"]
        root_path = os.path.join("path", "to")
        with mock.patch.object(
            BrukerMetadata, "list_scans", return_value=expected_keys
        ) as mock_list_scans, mock.patch.object(
            BrukerMetadata, "read_scan", return_value=None
        ) as mock_read_scan:
            m = BrukerMetadata(root_path)
            scans = m.read_scans()
            assert set(scans.keys()) == set(expected_keys)
            mock_list_scans.assert_called_once()
            mock_read_scan.assert_called()

    def test_parse_scans(self):
        root_path = os.path.join("path", "to")
        expected_contents = {"acqp": None, "method": None, "recons": None}
        with mock.patch.object(
            BrukerMetadata, "read_scans", return_value=expected_contents
        ) as mock_read_scans:
            m = BrukerMetadata(root_path)
            m.parse_scans()
            assert m.scan_data == expected_contents
            mock_read_scans.assert_called_once()

    def test_parse_subject(self):
        root_path = os.path.join("path", "to")
        expected_contents = {"OWNER": "nmrsu", "SUBJECT_name": "Tom Bombadil"}
        with mock.patch.object(
            BrukerMetadata, "read_subject", return_value=expected_contents
        ) as mock_read_subject:
            m = BrukerMetadata(root_path)
            m.parse_subject()
            assert m.subject_data == expected_contents
            mock_read_subject.assert_called_once()
