/*
A KBase module: kb_bedtools
*/

module kb_bedtools {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        App which takes a BAM file and returns a Fastq file
    */
    funcdef run_kb_bedtools(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

    /*
        App which takes GFF files and do the intersection command
    */
    funcdef run_kb_bedtools_intersect(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
