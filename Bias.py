# Copyright 2003 Yair Benita.  All rights reserved.
# This file is part of the Biopython distribution and governed by your
# choice of the "Biopython License Agreement" or the "BSD 3-Clause License".
# Please see the LICENSE file that should have been included as part of this
# package.
"""Methods for codon usage calculations."""


from __future__ import print_function

import math
from Bio.SeqUtils.CodonUsageIndices import SharpEcoliIndex
from Bio import SeqIO  # To parse a FASTA file


CodonsDict = {
    'TTT': 0, 'TTC': 0, 'TTA': 0, 'TTG': 0, 'CTT': 0,
    'CTC': 0, 'CTA': 0, 'CTG': 0, 'ATT': 0, 'ATC': 0,
    'ATA': 0, 'ATG': 0, 'GTT': 0, 'GTC': 0, 'GTA': 0,
    'GTG': 0, 'TAT': 0, 'TAC': 0, 'TAA': 0, 'TAG': 0,
    'CAT': 0, 'CAC': 0, 'CAA': 0, 'CAG': 0, 'AAT': 0,
    'AAC': 0, 'AAA': 0, 'AAG': 0, 'GAT': 0, 'GAC': 0,
    'GAA': 0, 'GAG': 0, 'TCT': 0, 'TCC': 0, 'TCA': 0,
    'TCG': 0, 'CCT': 0, 'CCC': 0, 'CCA': 0, 'CCG': 0,
    'ACT': 0, 'ACC': 0, 'ACA': 0, 'ACG': 0, 'GCT': 0,
    'GCC': 0, 'GCA': 0, 'GCG': 0, 'TGT': 0, 'TGC': 0,
    'TGA': 0, 'TGG': 0, 'CGT': 0, 'CGC': 0, 'CGA': 0,
    'CGG': 0, 'AGT': 0, 'AGC': 0, 'AGA': 0, 'AGG': 0,
    'GGT': 0, 'GGC': 0, 'GGA': 0, 'GGG': 0}


# this dictionary shows which codons encode the same AA
SynonymousCodons = {
    'CYS': ['TGT', 'TGC'],
    'ASP': ['GAT', 'GAC'],
    'SER': ['TCT', 'TCG', 'TCA', 'TCC', 'AGC', 'AGT'],
    'GLN': ['CAA', 'CAG'],
    'MET': ['ATG'],
    'ASN': ['AAC', 'AAT'],
    'PRO': ['CCT', 'CCG', 'CCA', 'CCC'],
    'LYS': ['AAG', 'AAA'],
    'STOP': ['TAG', 'TGA', 'TAA'],
    'THR': ['ACC', 'ACA', 'ACG', 'ACT'],
    'PHE': ['TTT', 'TTC'],
    'ALA': ['GCA', 'GCC', 'GCG', 'GCT'],
    'GLY': ['GGT', 'GGG', 'GGA', 'GGC'],
    'ILE': ['ATC', 'ATA', 'ATT'],
    'LEU': ['TTA', 'TTG', 'CTC', 'CTT', 'CTG', 'CTA'],
    'HIS': ['CAT', 'CAC'],
    'ARG': ['CGA', 'CGC', 'CGG', 'CGT', 'AGG', 'AGA'],
    'TRP': ['TGG'],
    'VAL': ['GTA', 'GTC', 'GTG', 'GTT'],
    'GLU': ['GAG', 'GAA'],
    'TYR': ['TAT', 'TAC']}


class CodonAdaptationIndex(object):
    """A codon adaptation index (CAI) implementation.

    Implements the codon adaptation index (CAI) described by Sharp and
    Li (Nucleic Acids Res. 1987 Feb 11;15(3):1281-95).

    NOTE - This implementation does not currently cope with alternative genetic
    codes: only the synonymous codons in the standard table are considered.
    """

    def __init__(self, file):
        """Initialize the class."""
        self.handle = file
        self.rcsu_index = {}
        self.nrcsu_index = {}
        self.codon_count = {}


    def generate_rcsu_index(self):
        """Generate a codon usage index from a FASTA file of CDS sequences.

        Takes a location of a Fasta file containing CDS sequences
        (which must all have a whole number of codons) and generates a codon
        usage index.

        RCSU values
        """
        # first make sure we're not overwriting an existing RSCU index:
        if self.rcsu_index != {}:
            raise ValueError("an RSCU index has already been set")
        # count codon occurrences in the file.
        self._count_codons(self.handle)

        # now to calculate the index we first need to sum the number of times
        # synonymous codons were used all together.
        for aa in SynonymousCodons:
            total = 0.0
            # RCSU values are CodonCount/((1/num of synonymous codons) * sum of
            # all synonymous codons)
            rcsu = []
            codons = SynonymousCodons[aa]

            for codon in codons:
                total += self.codon_count[codon]

            # calculate the RSCU value for each of the codons
            for codon in codons:
                denominator = float(total) / len(codons)
                rcsu.append(self.codon_count[codon] / denominator)

            # now generate the index W=RCSUi/RCSUmax:
            rcsu_max = max(rcsu)
            for codon_index, codon in enumerate(codons):
                self.rcsu_index[codon] = rcsu[codon_index]

    def generate_nrcsu_index(self):
        """Generate a codon usage index from a FASTA file of CDS sequences.

        Takes a location of a Fasta file containing CDS sequences
        (which must all have a whole number of codons) and generates a codon
        usage index.

        NRCSU values
        """
        # first make sure we're not overwriting an existing NRSCU index:
        if self.nrcsu_index != {}:
            raise ValueError("an NRSCU index has already been set")
        # count codon occurrences in the file.
        self._count_codons(self.handle)

        # now to calculate the index we first need to sum the number of times
        # synonymous codons were used all together.
        for aa in SynonymousCodons:
            total = 0.0
            # NRCSU values are CodonCount/sum of all synonymous codons
            nrcsu = []
            codons = SynonymousCodons[aa]

            for codon in codons:
                total += self.codon_count[codon]

            # calculate the NRSCU value for each of the codons
            for codon in codons:
                denominator = float(total)
                nrcsu.append(self.codon_count[codon] / denominator)

            # now generate the index W=RCSUi/RCSUmax:
            nrcsu_max = max(nrcsu)
            for codon_index, codon in enumerate(codons):
                self.nrcsu_index[codon] = nrcsu[codon_index]


    def _count_codons(self, fasta_file):
        with open(fasta_file, 'r') as handle:

            # make the codon dictionary local
            self.codon_count = CodonsDict.copy()

            # iterate over sequence and count all the codons in the FastaFile.
            for cur_record in SeqIO.parse(handle, "fasta"):
                # make sure the sequence is lower case
                if str(cur_record.seq).islower():
                    dna_sequence = str(cur_record.seq).upper()
                else:
                    dna_sequence = str(cur_record.seq)
                for i in range(0, len(dna_sequence), 3):
                    codon = dna_sequence[i:i + 3]
                    if codon in self.codon_count:
                        self.codon_count[codon] += 1
                    else:
                        raise TypeError("illegal codon %s in gene: %s"
                                        % (codon, cur_record.id))

    def print_rcsu_index(self):
        """Print out the index used.

        This just gives the index when the objects is printed.
        """
        for i in sorted(self.rcsu_index):
            print("%s\t%.3f" % (i, self.rcsu_index[i]))

    def print_nrcsu_index(self):
        """Print out the index used.

        This just gives the index when the objects is printed.
        """
        for i in sorted(self.nrcsu_index):
            print("%s\t%.3f" % (i, self.nrcsu_index[i]))