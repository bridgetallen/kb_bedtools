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

