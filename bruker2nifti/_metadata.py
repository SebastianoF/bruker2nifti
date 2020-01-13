"""
Provides the BrukerMetadata class for reading Bruker MRI metadata.

The BrukerMetadata class should be instantiated for each study. Dictionaries
are structured as follows:

subject_data {
  [key_from_subject_file]: [corresponding_value]
}

scan_data {
  [scan_number]: {
    'acqp': { [key_from_acqp_file]: [corresponding_value] },
    'method': { [key_from_method_file]: [corresponding_value] },
    'recons': {
      [recon_number]: {
        'reco': { [key_from_reco_file]: [corresponding_value] },
        'visu_pars': { [key_from_visu_pars_file]: [corresponding_value] }
      }
    }
  }
}

parse_subject() creates the subject_data dictionary and stores it in the object
parse_scans() creates the scan_data dictionary and stores it in the object

read_subject() returns a subject_data dictionary
read_scans() returns a scan_data dictionary
read_scan() returns the sub-dictionary corresponding to [scan_number]
read_recons() returns the sub-citionary corresponding to 'recons' for a given
  [scan_number]
read_recon() returns the sub-dictionary corresponding to [recon_number] for a
  given [scan_number]

list_scans() returns a list of scan numbers
list_recons() returns a list of recon numbers for a given scan
"""
import os

import bruker2nifti._utils as utils


class BrukerMetadata(object):
    """Represents metadata associated with a given MRI study."""

    def __init__(self, study):
        """
        Initialises a new object with the location of the study.

        self.pfo_input stores the path to the root directory of a give MRI
        study. The path is not checked for validity during initialisation.
        """
        self.pfo_input = study
        self.subject_data = None
        self.scan_data = None

    def parse_subject(self):
        """
        Stores subject metadata in the object.

        Reads the 'subject' file within the MRI study folder stores the
        metadata in `self.subject_data`.
        """
        self.subject_data = self.read_subject()

    def parse_scans(self):
        """
        Stores scan metadata in the object.

        Reads all 'acqp', 'method', 'reco' and 'visu_pars' files to get all
        scan metadata and store it in `self.study_data`.
        """
        self.scan_data = self.read_scans()

    def read_subject(self):
        """
        Reads metadata from the 'subject' file and returns a dictionary.

        Reads the 'subject' metadata file within the root study folder. It
        populates a dictionary with the data where keys correspond to variables
        within the source file (minus any ##/$/PVM_ decorators).
        """
        return utils.bruker_read_files("subject", self.pfo_input)

    def read_scans(self):
        """
        Reads metadata for all scans of a study and returns a dictionary.

        Reads all 'acqp', 'method', 'reco' and 'visu_pars' files for the study
        and returns a nested dictionary containing all variables and their
        values specified in those files.
        """
        return {scan: self.read_scan(scan) for scan in self.list_scans()}

    def read_scan(self, scan):
        """
        Reads the metadata for a specified scan and returns a dictionary.

        Reads 'acqp', 'method' and all 'reco' and 'visu_pars' files for a given
        scan and its reconstructions. A dictionary of these values is returned.
        The top level keys are 'acqp', 'method' and 'recons' where 'recons' is
        sub-keyed with individual recon numbers, each of which is in turn keyed
        with 'reco' and 'visu_pars'. Beneath the appropriate key is a
        sub-dictionary keyed with variables from the source file (minus and
        ##/$/PVM_ decorators).
        """
        scan_data = {}
        data_path = os.path.join(self.pfo_input, scan)
        scan_data["acqp"] = utils.bruker_read_files("acqp", data_path)
        scan_data["method"] = utils.bruker_read_files("method", data_path)
        scan_data["recons"] = self.read_recons(scan)
        return scan_data

    def read_recons(self, scan):
        """
        Reads the metadata for all recons and returns a dictionary.

        Reads 'reco' and 'visu_pars' files from all recon sub-folders for the
        given scan. The metadata is stored in a dictionary with top level
        keys corresponding to reconstruction numbers.
        """
        recon_data = {}
        for recon in self.list_recons(scan):
            recon_data[recon] = self.read_recon(scan, recon)
        return recon_data

    def read_recon(self, scan, recon):
        """
        Reads the metadata from a specified recon and returns a dictionary.

        Reads the 'reco' and 'visu_pars' files from within a specific
        reconstruction sub-directory and compiles a dictionary. At the top
        level the dictionary has keys corresponding to the two files and then
        the sub-dictionaries are keyed according to variables in the relevant
        file (minus any ##/$/PVM_ decorators).
        """
        recon_data = {}
        data_path = os.path.join(self.pfo_input, scan)
        recon_data["reco"] = utils.bruker_read_files("reco", data_path, recon)
        recon_data["visu_pars"] = utils.bruker_read_files("visu_pars", data_path, recon)
        return recon_data

    def list_scans(self):
        """
        Returns a list of scans that comprise this study.

        Returns a list of strings corresponding to the numbered sub-directories
        of the root study folder. Each of these sub-directories stores data for
        an individual scan.

        Note this function doesn't read the contents of the scan directories to
        confirm that they contain valid scan data.
        """
        return self._list_subdirs(self.pfo_input)

    def list_recons(self, scan):
        """
        Returns a list of recons for a given scan within this study.

        Returns a list of strings corresponding to the numbered sub-directories
        of the pdata sub-directory within the scan folder. Each of these
        sub-directories stores data for an individual reconstruction.

        Note this function doesn't read the contents of the reconstruction
        directories to confirm that they contain valid reconstruction data.
        """
        pfo_recons = os.path.join(self.pfo_input, scan, "pdata")
        return self._list_subdirs(pfo_recons)

    def _list_subdirs(self, path):
        """
        Return a list of scan or reconstruction sub-directories.

        Return a sorted list of strings corresponding to sub-directories of the
        given path that could be either a scan or reconstruction. This is based
        on the bruker convention of naming these as an integer.

        Note this function does not read the contents of directories to confirm
        that they contain scan or reconstruction data.
        """
        dirs = [
            d
            for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d)) and d.isdigit()
        ]
        return sorted(dirs, key=int)
