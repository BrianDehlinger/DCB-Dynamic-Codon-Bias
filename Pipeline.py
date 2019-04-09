import abc
import Bias
from Bio import SeqIO
import pandas
from NCBIGet import get_accession_data
import os

class GeneralPipeline(abc.ABC):
    def __init__(self):
        self.file = ''

    ### Concrete method that should take fasta input files of the list of genes. We can code and test this now.
    def get_bias(self, fasta):
        print("get_bias has been called")
        index = CodonUsageTable(fasta)
        index.generate_rcsu_table()
        index.generate_nrcsu_table()
        index.generate_hegfb_table()
        data = [index.rcsu_index, index.nrcsu_index, index.hegfb_index]
        return data

    @abc.abstractmethod
    ### This will vary. So far we have NCBI and a genome.
    def get_data(self):
        pass

    @abc.abstractmethod
    def get_hegs(self):
        pass

    ## Concrete method that should be the same for all pipelines.
    def output(self):
        print("output has been called")


class NcbiPipe(GeneralPipeline):
    
    ## This function downloads the genome from a refseq accession number
    def get_data(self, accession):
        self.file = "temp/" + get_accession_data(accession)

    def get_hegs(self):
        os.system("./diamond blastx -d testDB -q " + self.file + " -o temp/matches -f 6 stitle bitscore qseqid") 

    def clean_hegs(self):
        df = pandas.read_table("temp/matches", names=["Subject", "Bit", "SeqID"], skipinitialspace=True)
        df = df.replace('\[.*\]', '', regex=True)
        df["Subject"] = df["Subject"].str.strip()
        df["Subject"] = df["Subject"].apply(lambda x: ' '.join(x.split(' ')[1:]))
        df = df.replace("elongation factor EF-2", "elongation factor G")
        df2 = df.sort_values(["Subject", "Bit"], ascending=[True,False])
        df2 = df2.loc[df2.groupby('Subject')["Bit"].idxmax()].reset_index(drop=True)
        items = df2.SeqID.unique()
        newSeqs = []
        for seq_record in SeqIO.parse("theCDS", "fasta"):
            if (seq_record.id in items):
                newSeqs.append(seq_record)
        print(newSeqs)

        with open("temp/temporary.fasta", "w") as handle:
            SeqIO.write(newSeqs, handle, "fasta")




class Facade:

    def uploaded_genome(self, file):    
        print("The genome was successfully uploaded")   

    def ncbi(self, accession):
        print(accession)


testPipe = NcbiPipe()
testPipe.get_data("APNU00000000")
testPipe.get_hegs()
testPipe.clean_hegs()


