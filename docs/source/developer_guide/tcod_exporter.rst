Exporting structures to TCOD
----------------------------

Export of
:py:class:`StructureData <aiida.orm.data.structure.StructureData>` and
:py:class:`CifData <aiida.orm.data.cif.CifData>` (or any other data type,
which can be converted to them) to the
`Theoretical Crystallography Open Database`_ (TCOD) can be divided into
following workflow steps:

=== =============================== ================================================================== ================================================================== ====== ============
No. Description                     Input                                                              Output                                                             Type   Implemented?
=== =============================== ================================================================== ================================================================== ====== ============
0   Conversion of the StructureData :py:class:`StructureData <aiida.orm.data.structure.StructureData>` :py:class:`CifData <aiida.orm.data.cif.CifData>`                   Inline \+
    to CifData
1   Detection of the symmetry and   :py:class:`CifData <aiida.orm.data.cif.CifData>`                   :py:class:`CifData <aiida.orm.data.cif.CifData>`                   Inline \+
    reduction to the unit cell
2   Niggli reduction of the unit    :py:class:`CifData <aiida.orm.data.cif.CifData>`                   :py:class:`CifData <aiida.orm.data.cif.CifData>`                   Inline ---
    cell
3   Addition of structure           :py:class:`CifData <aiida.orm.data.cif.CifData>`,                  :py:class:`CifData <aiida.orm.data.cif.CifData>`                   Inline PW and CP
    properties (total energy,       :py:class:`ParameterData <aiida.orm.data.parameter.ParameterData>`
    residual forces)
4   Addition of the metadata for    :py:class:`CifData <aiida.orm.data.cif.CifData>`                   :py:class:`CifData <aiida.orm.data.cif.CifData>`                   Inline ~
    reproduction of the results
5   Depostition to the TCOD         :py:class:`CifData <aiida.orm.data.cif.CifData>`                   :py:class:`ParameterData <aiida.orm.data.parameter.ParameterData>` Job    \+
=== =============================== ================================================================== ================================================================== ====== ============

Type of each step's calculation
(:py:class:`InlineCalculation <aiida.orm.calculation.inline.InlineCalculation>`
or :py:class:`JobCalculation <aiida.orm.calculation.job.JobCalculation>`)
defined in column *Type*. Each step is described in more detail below:

* Conversion of the StructureData to CifData
    Conversion between the
    :py:class:`StructureData <aiida.orm.data.structure.StructureData>` and
    :py:class:`CifData <aiida.orm.data.cif.CifData>` is done via
    ASE atoms object.
* Detection of the symmetry and reduction to the unit cell
    Detection of the symmetry and reduction to the unit cell is performed
    using `pyspglib.spglib.refine_cell() function`_.
* Niggli reduction of the unit cell
    Reduction of the unit cell to Niggli cell is a *nice to have* feature,
    as it would allow to represent structure as an unambiguously selected
    unit cell.
* Addition of structure properties (energy, remaining forces)
    The structure properties from the calculations, such as total energy
    and residual forces can be extracted from
    :py:class:`ParameterData <aiida.orm.data.parameter.ParameterData>`
    nodes and put into related `TCOD CIF dictionaries`_ tags using
    calculation-specific parameter translator, derived from
    :py:class:`BaseTcodtranslator <aiida.tools.dbexporters.tcod_plugins.BaseTcodtranslator>`.
* Addition of the metadata for reproduction of the results
    Current metadata, added for reproducibility, includes scripts for
    re-running of calculations, outputs from the calculations and exported
    subset of AiiDA database. It's not quite clear what/how to record the
    metadata for calculations of type
    :py:class:`InlineCalculation <aiida.orm.calculation.inline.InlineCalculation>`.
* Depostition to the TCOD
    Deposition of the final
    :py:class:`CifData <aiida.orm.data.cif.CifData>` to the TCOD is
    performed using
    :ref:`cif_cod_deposit script from cod-tools package <codtools_cifcoddeposit>`.

.. _Theoretical Crystallography Open Database: http://www.crystallography.net/tcod/
.. _pyspglib.spglib.refine_cell() function: http://spglib.sourceforge.net/api.html#spg-refine-cell
.. _TCOD CIF dictionaries: http://www.crystallography.net/tcod/cif/dictionaries/
