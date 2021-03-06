#!/usr/bin/env python
"""Convert a GFF and associated FASTA file into GenBank format.

Usage:
    gff_to_genbank.py <GFF annotation file> <FASTA sequence file>
"""
import sys
import os

from Bio import SeqIO
from Bio.Alphabet import generic_dna
from Bio import Seq

from BCBio import GFF

def main(gff_file, fasta_file):
    out_file = "%s.gb" % os.path.splitext(gff_file)[0]
    fasta_input = SeqIO.to_dict(_fix_ncbi_id(
        SeqIO.parse(fasta_file, "fasta", generic_dna)))
    gff_iter = GFF.parse(gff_file, fasta_input)
    SeqIO.write(_check_gff(gff_iter), out_file, "genbank")

def _fix_ncbi_id(fasta_iter):
    """GenBank identifiers can only be 16 characters; try to shorten NCBI.
    """
    for rec in fasta_iter:
        if len(rec.name) > 16 and rec.name.find("|") > 0:
            new_id = [x for x in rec.name.split("|") if x][-1]
            print "Warning: shortening NCBI name %s to %s" % (rec.id, new_id)
            rec.id = new_id
            rec.name = new_id
            yield rec

def _check_gff(gff_iterator):
    """Check GFF files before feeding to SeqIO to be sure they have sequences.
    """
    for rec in gff_iterator:
        if isinstance(rec.seq, Seq.UnknownSeq):
            print "Warning: FASTA sequence not found for '%s' in GFF file" % (
                    rec.id)
            rec.seq.alphabet = generic_dna
        yield rec

if __name__ == "__main__":
    main(*sys.argv[1:])
