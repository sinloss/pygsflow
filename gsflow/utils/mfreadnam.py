"""
mfreadnam module.  Contains the NamData class. Note that the user can access
the NamData class as `flopy.modflow.NamData`.

Additional information about the MODFLOW name file can be found at the `Online
MODFLOW Guide
<http://water.usgs.gov/ogw/modflow/MODFLOW-2005-Guide/name_file.htm>`_.

"""
import os
import sys
from .gsflow_io import get_file_abs
from flopy.utils.mfreadnam import NamData as fpNamData
from flopy.utils.mfreadnam import attribs_from_namfile_header as fp_attribs


if sys.version_info < (3, 6):
    from collections import OrderedDict

    dict = OrderedDict


class NamData(fpNamData):
    """
    Child class of the MODFLOW Namefile Class.

    Parameters
    ----------
    pkgtype : string
        String identifying the type of MODFLOW package. See the
        mfnam_packages dictionary keys in the model object for a list
        of supported packages. This dictionary is also passed in as packages.
    name : string
        Filename of the package file identified in the name file
    handle : file handle
        File handle referring to the file identified by `name`
    packages : dictionary
        Dictionary of package objects as defined in the
        `mfnam_packages` attribute of :class:`flopy.modflow.mf.Modflow`.

    Attributes
    ----------
    filehandle : file handle
        File handle to the package file. Read from `handle`.
    filename : string
        Filename of the package file identified in the name file.
        Read from `name`.
    filetype : string
        String identifying the type of MODFLOW package. Read from
        `pkgtype`.
    package : string
        Package type. Only assigned if `pkgtype` is found in the keys
        of `packages`

    Methods
    -------

    See Also
    --------

    Notes
    -----

    Examples
    --------

    """

    def __init__(self, pkgtype, name, handle, packages):
        super(NamData, self).__init__(pkgtype, name, handle, packages)


def getfiletypeunit(nf, filetype):
    """
    Method to return unit number of a package from a NamData instance

    Parameters
    ----------
    nf : NamData instance
    filetype : string, name of package seeking information for

    Returns
    -------
    cunit : int, unit number corresponding to the package type

    """
    for cunit, cvals in nf.items():
        if cvals.filetype.lower() == filetype.lower():
            return cunit
    print('Name file does not contain file of type "{0}"'.format(filetype))
    return None


def parsenamefile(
    namfilename, packages, control_file=None, verbose=True, model_ws="."
):
    """
    Returns dict from the nam file with NamData keyed by unit number

    Parameters
    ----------
    namfilename : str
        Name of the MODFLOW namefile to parse.
    packages : dict
        Dictionary of package objects as defined in the `mfnam_packages`
        attribute of :class:`flopy.modflow.mf.Modflow`.
    control_file : str
        gsflow option for creating absolute paths to read the nam file
    verbose : bool
        Print messages to screen.  Default is True.

    Returns
    -------
    dict or OrderedDict
        For each file listed in the name file, a
        :class:`flopy.utils.mfreadnam.NamData` instance
        is stored in the returned dict keyed by unit number. Prior to Python
        version 3.6 the return object is an OrderedDict to retain the order
        of items in the nam file.

    Raises
    ------
    IOError:
        If namfilename does not exist in the directory.
    ValueError:
        For lines that cannot be parsed.

    """
    # initiate the ext_unit_dict ordered dictionary
    ext_unit_dict = dict()

    if verbose:
        print("Parsing the namefile --> {0:s}".format(namfilename))

    if not os.path.isfile(namfilename):
        # help diagnose the namfile and directory
        raise IOError(
            "Could not find {} in directory {}".format(
                namfilename, os.path.dirname(namfilename)
            )
        )
    with open(namfilename, "r") as fp:
        lines = fp.readlines()

    for ln, line in enumerate(lines, 1):
        line = line.strip()
        if len(line) == 0 or line.startswith("#"):
            # skip blank lines or comments
            continue
        items = line.split()
        # ensure we have at least three items
        if len(items) < 3:
            raise ValueError(
                "line number {} has fewer than 3 items: {}".format(ln, line)
            )
        ftype, key, fpath = items[0:3]
        ftype = ftype.upper()

        # remove quotes in file path
        if '"' in fpath:
            fpath = fpath.replace('"', "")
        if "'" in fpath:
            fpath = fpath.replace("'", "")

        # need make filenames with paths system agnostic
        if "/" in fpath:
            raw = fpath.split("/")
        elif "\\" in fpath:
            raw = fpath.split("\\")
        else:
            raw = [fpath]
        fpath = os.path.join(*raw)

        # update for GSFLOW
        if control_file is None:
            fname = os.path.join(model_ws, fpath)
        else:
            # if the user supplies a control_file, then it builds the absolute path
            fname = get_file_abs(control_file=control_file, fn=fpath)

        if not os.path.isfile(fname) or not os.path.exists(fname):
            # change to lower and make comparison (required for linux)
            dn = os.path.dirname(fname)
            fls = os.listdir(dn)
            lownams = [f.lower() for f in fls]
            bname = os.path.basename(fname)
            if bname.lower() in lownams:
                idx = lownams.index(bname.lower())
                fname = os.path.join(dn, fls[idx])
        # open the file
        openmode = "r"
        if ftype == "DATA(BINARY)":
            openmode = "rb"
        try:
            filehandle = open(fname, openmode)
        except IOError:
            if verbose:
                print("could not set filehandle to {0:s}".format(fpath))
            filehandle = None
        # be sure the second value is an integer
        try:
            key = int(key)
        except ValueError:
            raise ValueError(
                "line number {}: the unit number (second item) "
                "is not an integer: {}".format(ln, line)
            )
        # Trap for the case where unit numbers are specified as zero
        # In this case, the package must have a variable called
        # unit number attached to it.  If not, then the key is set
        # to fname
        if key == 0:
            ftype_lower = ftype.lower()
            if ftype_lower in packages:
                key = packages[ftype_lower].reservedunit()
            else:
                key = ftype
        ext_unit_dict[key] = NamData(ftype, fname, filehandle, packages)
    return ext_unit_dict


def attribs_from_namfile_header(namefile):
    return fp_attribs(namefile)
