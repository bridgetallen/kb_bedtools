import logging
import subprocess
import os
import pytest
from kb_bedtools.utils import BamConversion, Intersection 


@pytest.fixture
def process():
    return subprocess.Popen(
        ["echo", "hello world"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def test_process(process):
    logging.info("Running a test")
    assert 1 == 1

def test_bam_to_fastq_creates_output(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    bam_path = os.path.join(os.path.dirname(__file__), "..", "minimal.bam")

    result_path = BamConversion.bam_to_fastq(bam_path, str(output_dir))

    assert os.path.exists(result_path), "FASTQ output file was not created"
    with open(result_path) as f:
        contents = f.read()
    assert contents.startswith("@"), "FASTQ output does not appear valid"

def test_bam_to_fastq_invalid_input_raises():
    with pytest.raises(Exception):
        BamConversion.bam_to_fastq("/invalid/path/to/file.bam")

def test_bam_to_fastq_empty_file_raises(tmp_path):
    empty_bam = tmp_path / "empty.bam"
    empty_bam.touch()

    with pytest.raises(Exception):
        BamConversion.bam_to_fastq(str(empty_bam), str(tmp_path))


def test_bam_to_fastq_multiple_outputs(tmp_path):
    bam_path = os.path.join(os.path.dirname(__file__), "..", "minimal.bam")

    result1 = BamConversion.bam_to_fastq(bam_path, tmp_path)
    result2 = BamConversion.bam_to_fastq(bam_path, tmp_path)

    assert result1 != result2, "Multiple conversions should create unique output files"

def test_bam_to_fastq_paired_end_output(tmp_path):
    bam_path = os.path.join(os.path.dirname(__file__), "..", "minimal.bam")

    result_paths = BamConversion.bam_to_fastq_paired(
        bam_file=bam_path,
        shared_folder=str(tmp_path)
    )

    try:
        
        assert isinstance(result_paths, dict), "Output should be a dictionary"
        assert "read1" in result_paths and "read2" in result_paths, "Missing paired-end keys"
        assert os.path.exists(result_paths["read1"]), "FASTQ for read 1 not created"
        assert os.path.exists(result_paths["read2"]), "FASTQ for read 2 not created"


        with open(result_paths["read1"]) as f1, open(result_paths["read2"]) as f2:
            content1 = f1.read(1)
            content2 = f2.read(1)

            if content1:
                assert content1 == "@", "Read 1 output is not a valid FASTQ file"
            else:
                print("Warning: Read 1 FASTQ file is empty")

            if content2:
                assert content2 == "@", "Read 2 output is not a valid FASTQ file"
            else:
                print ("Warning: Read 2 FASTQ file is empty")

    finally:
        for path in result_paths.values():
            if os.path.exists(path):
                os.remove(path)
