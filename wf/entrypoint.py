from dataclasses import dataclass
from enum import Enum
import os
import subprocess
import requests
import shutil
from pathlib import Path
import typing
import typing_extensions

from latch.resources.workflow import workflow
from latch.resources.tasks import nextflow_runtime_task, custom_task
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir
from latch.ldata.path import LPath
from latch_cli.nextflow.workflow import get_flag
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.utils import urljoins
from latch.types import metadata
from flytekit.core.annotation import FlyteAnnotation

from latch_cli.services.register.utils import import_module_by_path

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)
import latch_metadata

@custom_task(cpu=0.25, memory=0.5, storage_gib=1)
def initialize() -> str:
    token = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID")
    if token is None:
        raise RuntimeError("failed to get execution token")

    headers = {"Authorization": f"Latch-Execution-Token {token}"}

    print("Provisioning shared storage volume... ", end="")
    resp = requests.post(
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage",
        headers=headers,
        json={
            "storage_gib": 100,
        }
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]






@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(pvc_name: str, input: LatchFile, databases: LatchFile, save_untarred_databases: typing.Optional[bool], outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], skip_preprocessing_qc: typing.Optional[bool], save_preprocessed_reads: typing.Optional[bool], save_analysis_ready_fastqs: typing.Optional[bool], perform_shortread_qc: typing.Optional[bool], shortread_qc_skipadaptertrim: typing.Optional[bool], shortread_qc_adapter1: typing.Optional[str], shortread_qc_adapter2: typing.Optional[str], shortread_qc_adapterlist: typing.Optional[str], shortread_qc_mergepairs: typing.Optional[bool], shortread_qc_includeunmerged: typing.Optional[bool], shortread_qc_dedup: typing.Optional[bool], perform_shortread_complexityfilter: typing.Optional[bool], shortread_complexityfilter_bbduk_mask: typing.Optional[bool], save_complexityfiltered_reads: typing.Optional[bool], perform_longread_qc: typing.Optional[bool], longread_qc_skipadaptertrim: typing.Optional[bool], longread_qc_skipqualityfilter: typing.Optional[bool], perform_shortread_hostremoval: typing.Optional[bool], perform_longread_hostremoval: typing.Optional[bool], hostremoval_reference: typing.Optional[str], shortread_hostremoval_index: typing.Optional[str], longread_hostremoval_index: typing.Optional[str], save_hostremoval_index: typing.Optional[bool], save_hostremoval_bam: typing.Optional[bool], save_hostremoval_unmapped: typing.Optional[bool], perform_runmerging: typing.Optional[bool], save_runmerged_reads: typing.Optional[bool], run_centrifuge: typing.Optional[bool], centrifuge_save_reads: typing.Optional[bool], run_diamond: typing.Optional[bool], diamond_save_reads: typing.Optional[bool], run_kaiju: typing.Optional[bool], kaiju_expand_viruses: typing.Optional[bool], run_kraken2: typing.Optional[bool], kraken2_save_reads: typing.Optional[bool], kraken2_save_readclassifications: typing.Optional[bool], kraken2_save_minimizers: typing.Optional[bool], run_krakenuniq: typing.Optional[bool], krakenuniq_save_reads: typing.Optional[bool], krakenuniq_save_readclassifications: typing.Optional[bool], run_bracken: typing.Optional[bool], run_malt: typing.Optional[bool], malt_save_reads: typing.Optional[bool], malt_generate_megansummary: typing.Optional[bool], run_metaphlan: typing.Optional[bool], run_motus: typing.Optional[bool], motus_use_relative_abundance: typing.Optional[bool], motus_save_mgc_read_counts: typing.Optional[bool], motus_remove_ncbi_ids: typing.Optional[bool], run_kmcp: typing.Optional[bool], kmcp_save_search: typing.Optional[bool], run_ganon: typing.Optional[bool], ganon_save_readclassifications: typing.Optional[bool], ganon_report_rank: typing.Optional[str], run_profile_standardisation: typing.Optional[bool], standardisation_motus_generatebiom: typing.Optional[bool], run_krona: typing.Optional[bool], krona_taxonomy_directory: typing.Optional[str], taxpasta_taxonomy_dir: typing.Optional[str], taxpasta_add_name: typing.Optional[bool], taxpasta_add_rank: typing.Optional[bool], taxpasta_add_lineage: typing.Optional[bool], taxpasta_add_idlineage: typing.Optional[bool], taxpasta_add_ranklineage: typing.Optional[bool], taxpasta_ignore_errors: typing.Optional[bool], multiqc_methods_description: typing.Optional[str], preprocessing_qc_tool: typing.Optional[str], shortread_qc_tool: typing.Optional[str], shortread_qc_minlength: typing.Optional[int], shortread_complexityfilter_tool: typing.Optional[str], shortread_complexityfilter_entropy: typing.Optional[float], shortread_complexityfilter_bbduk_windowsize: typing.Optional[int], shortread_complexityfilter_fastp_threshold: typing.Optional[int], shortread_complexityfilter_prinseqplusplus_mode: typing.Optional[str], shortread_complexityfilter_prinseqplusplus_dustscore: typing.Optional[float], longread_qc_qualityfilter_minlength: typing.Optional[int], longread_qc_qualityfilter_keeppercent: typing.Optional[int], longread_qc_qualityfilter_targetbases: typing.Optional[int], diamond_output_format: typing.Optional[str], kaiju_taxon_rank: typing.Optional[str], krakenuniq_ram_chunk_size: typing.Optional[str], krakenuniq_batch_size: typing.Optional[int], malt_mode: typing.Optional[str], kmcp_mode: typing.Optional[int], ganon_report_type: typing.Optional[str], ganon_report_toppercentile: typing.Optional[int], ganon_report_mincount: typing.Optional[int], ganon_report_maxcount: typing.Optional[int], standardisation_taxpasta_format: typing.Optional[str]) -> None:
    try:
        shared_dir = Path("/nf-workdir")



        ignore_list = [
            "latch",
            ".latch",
            "nextflow",
            ".nextflow",
            "work",
            "results",
            "miniconda",
            "anaconda3",
            "mambaforge",
        ]

        shutil.copytree(
            Path("/root"),
            shared_dir,
            ignore=lambda src, names: ignore_list,
            ignore_dangling_symlinks=True,
            dirs_exist_ok=True,
        )

        cmd = [
            "/root/nextflow",
            "run",
            str(shared_dir / "main.nf"),
            "-work-dir",
            str(shared_dir),
            "-profile",
            "docker",
            "-c",
            "latch.config",
                *get_flag('input', input),
                *get_flag('databases', databases),
                *get_flag('save_untarred_databases', save_untarred_databases),
                *get_flag('outdir', outdir),
                *get_flag('email', email),
                *get_flag('multiqc_title', multiqc_title),
                *get_flag('skip_preprocessing_qc', skip_preprocessing_qc),
                *get_flag('preprocessing_qc_tool', preprocessing_qc_tool),
                *get_flag('save_preprocessed_reads', save_preprocessed_reads),
                *get_flag('save_analysis_ready_fastqs', save_analysis_ready_fastqs),
                *get_flag('perform_shortread_qc', perform_shortread_qc),
                *get_flag('shortread_qc_tool', shortread_qc_tool),
                *get_flag('shortread_qc_skipadaptertrim', shortread_qc_skipadaptertrim),
                *get_flag('shortread_qc_adapter1', shortread_qc_adapter1),
                *get_flag('shortread_qc_adapter2', shortread_qc_adapter2),
                *get_flag('shortread_qc_adapterlist', shortread_qc_adapterlist),
                *get_flag('shortread_qc_mergepairs', shortread_qc_mergepairs),
                *get_flag('shortread_qc_includeunmerged', shortread_qc_includeunmerged),
                *get_flag('shortread_qc_minlength', shortread_qc_minlength),
                *get_flag('shortread_qc_dedup', shortread_qc_dedup),
                *get_flag('perform_shortread_complexityfilter', perform_shortread_complexityfilter),
                *get_flag('shortread_complexityfilter_tool', shortread_complexityfilter_tool),
                *get_flag('shortread_complexityfilter_entropy', shortread_complexityfilter_entropy),
                *get_flag('shortread_complexityfilter_bbduk_windowsize', shortread_complexityfilter_bbduk_windowsize),
                *get_flag('shortread_complexityfilter_bbduk_mask', shortread_complexityfilter_bbduk_mask),
                *get_flag('shortread_complexityfilter_fastp_threshold', shortread_complexityfilter_fastp_threshold),
                *get_flag('shortread_complexityfilter_prinseqplusplus_mode', shortread_complexityfilter_prinseqplusplus_mode),
                *get_flag('shortread_complexityfilter_prinseqplusplus_dustscore', shortread_complexityfilter_prinseqplusplus_dustscore),
                *get_flag('save_complexityfiltered_reads', save_complexityfiltered_reads),
                *get_flag('perform_longread_qc', perform_longread_qc),
                *get_flag('longread_qc_skipadaptertrim', longread_qc_skipadaptertrim),
                *get_flag('longread_qc_skipqualityfilter', longread_qc_skipqualityfilter),
                *get_flag('longread_qc_qualityfilter_minlength', longread_qc_qualityfilter_minlength),
                *get_flag('longread_qc_qualityfilter_keeppercent', longread_qc_qualityfilter_keeppercent),
                *get_flag('longread_qc_qualityfilter_targetbases', longread_qc_qualityfilter_targetbases),
                *get_flag('perform_shortread_hostremoval', perform_shortread_hostremoval),
                *get_flag('perform_longread_hostremoval', perform_longread_hostremoval),
                *get_flag('hostremoval_reference', hostremoval_reference),
                *get_flag('shortread_hostremoval_index', shortread_hostremoval_index),
                *get_flag('longread_hostremoval_index', longread_hostremoval_index),
                *get_flag('save_hostremoval_index', save_hostremoval_index),
                *get_flag('save_hostremoval_bam', save_hostremoval_bam),
                *get_flag('save_hostremoval_unmapped', save_hostremoval_unmapped),
                *get_flag('perform_runmerging', perform_runmerging),
                *get_flag('save_runmerged_reads', save_runmerged_reads),
                *get_flag('run_centrifuge', run_centrifuge),
                *get_flag('centrifuge_save_reads', centrifuge_save_reads),
                *get_flag('run_diamond', run_diamond),
                *get_flag('diamond_output_format', diamond_output_format),
                *get_flag('diamond_save_reads', diamond_save_reads),
                *get_flag('run_kaiju', run_kaiju),
                *get_flag('kaiju_expand_viruses', kaiju_expand_viruses),
                *get_flag('kaiju_taxon_rank', kaiju_taxon_rank),
                *get_flag('run_kraken2', run_kraken2),
                *get_flag('kraken2_save_reads', kraken2_save_reads),
                *get_flag('kraken2_save_readclassifications', kraken2_save_readclassifications),
                *get_flag('kraken2_save_minimizers', kraken2_save_minimizers),
                *get_flag('run_krakenuniq', run_krakenuniq),
                *get_flag('krakenuniq_save_reads', krakenuniq_save_reads),
                *get_flag('krakenuniq_ram_chunk_size', krakenuniq_ram_chunk_size),
                *get_flag('krakenuniq_save_readclassifications', krakenuniq_save_readclassifications),
                *get_flag('krakenuniq_batch_size', krakenuniq_batch_size),
                *get_flag('run_bracken', run_bracken),
                *get_flag('run_malt', run_malt),
                *get_flag('malt_mode', malt_mode),
                *get_flag('malt_save_reads', malt_save_reads),
                *get_flag('malt_generate_megansummary', malt_generate_megansummary),
                *get_flag('run_metaphlan', run_metaphlan),
                *get_flag('run_motus', run_motus),
                *get_flag('motus_use_relative_abundance', motus_use_relative_abundance),
                *get_flag('motus_save_mgc_read_counts', motus_save_mgc_read_counts),
                *get_flag('motus_remove_ncbi_ids', motus_remove_ncbi_ids),
                *get_flag('run_kmcp', run_kmcp),
                *get_flag('kmcp_mode', kmcp_mode),
                *get_flag('kmcp_save_search', kmcp_save_search),
                *get_flag('run_ganon', run_ganon),
                *get_flag('ganon_save_readclassifications', ganon_save_readclassifications),
                *get_flag('ganon_report_type', ganon_report_type),
                *get_flag('ganon_report_rank', ganon_report_rank),
                *get_flag('ganon_report_toppercentile', ganon_report_toppercentile),
                *get_flag('ganon_report_mincount', ganon_report_mincount),
                *get_flag('ganon_report_maxcount', ganon_report_maxcount),
                *get_flag('run_profile_standardisation', run_profile_standardisation),
                *get_flag('standardisation_motus_generatebiom', standardisation_motus_generatebiom),
                *get_flag('run_krona', run_krona),
                *get_flag('krona_taxonomy_directory', krona_taxonomy_directory),
                *get_flag('standardisation_taxpasta_format', standardisation_taxpasta_format),
                *get_flag('taxpasta_taxonomy_dir', taxpasta_taxonomy_dir),
                *get_flag('taxpasta_add_name', taxpasta_add_name),
                *get_flag('taxpasta_add_rank', taxpasta_add_rank),
                *get_flag('taxpasta_add_lineage', taxpasta_add_lineage),
                *get_flag('taxpasta_add_idlineage', taxpasta_add_idlineage),
                *get_flag('taxpasta_add_ranklineage', taxpasta_add_ranklineage),
                *get_flag('taxpasta_ignore_errors', taxpasta_ignore_errors),
                *get_flag('multiqc_methods_description', multiqc_methods_description)
        ]

        print("Launching Nextflow Runtime")
        print(' '.join(cmd))
        print(flush=True)

        env = {
            **os.environ,
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms2048M -Xmx8G -XX:ActiveProcessorCount=4",
            "K8S_STORAGE_CLAIM_NAME": pvc_name,
            "NXF_DISABLE_CHECK_LATEST": "true",
        }
        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            name = _get_execution_name()
            if name is None:
                print("Skipping logs upload, failed to get execution name")
            else:
                remote = LPath(urljoins("latch:///your_log_dir/nf_nf_core_taxprofiler", name, "nextflow.log"))
                print(f"Uploading .nextflow.log to {remote.path}")
                remote.upload_from(nextflow_log)



@workflow(metadata._nextflow_metadata)
def nf_nf_core_taxprofiler(input: LatchFile, databases: LatchFile, save_untarred_databases: typing.Optional[bool], outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], skip_preprocessing_qc: typing.Optional[bool], save_preprocessed_reads: typing.Optional[bool], save_analysis_ready_fastqs: typing.Optional[bool], perform_shortread_qc: typing.Optional[bool], shortread_qc_skipadaptertrim: typing.Optional[bool], shortread_qc_adapter1: typing.Optional[str], shortread_qc_adapter2: typing.Optional[str], shortread_qc_adapterlist: typing.Optional[str], shortread_qc_mergepairs: typing.Optional[bool], shortread_qc_includeunmerged: typing.Optional[bool], shortread_qc_dedup: typing.Optional[bool], perform_shortread_complexityfilter: typing.Optional[bool], shortread_complexityfilter_bbduk_mask: typing.Optional[bool], save_complexityfiltered_reads: typing.Optional[bool], perform_longread_qc: typing.Optional[bool], longread_qc_skipadaptertrim: typing.Optional[bool], longread_qc_skipqualityfilter: typing.Optional[bool], perform_shortread_hostremoval: typing.Optional[bool], perform_longread_hostremoval: typing.Optional[bool], hostremoval_reference: typing.Optional[str], shortread_hostremoval_index: typing.Optional[str], longread_hostremoval_index: typing.Optional[str], save_hostremoval_index: typing.Optional[bool], save_hostremoval_bam: typing.Optional[bool], save_hostremoval_unmapped: typing.Optional[bool], perform_runmerging: typing.Optional[bool], save_runmerged_reads: typing.Optional[bool], run_centrifuge: typing.Optional[bool], centrifuge_save_reads: typing.Optional[bool], run_diamond: typing.Optional[bool], diamond_save_reads: typing.Optional[bool], run_kaiju: typing.Optional[bool], kaiju_expand_viruses: typing.Optional[bool], run_kraken2: typing.Optional[bool], kraken2_save_reads: typing.Optional[bool], kraken2_save_readclassifications: typing.Optional[bool], kraken2_save_minimizers: typing.Optional[bool], run_krakenuniq: typing.Optional[bool], krakenuniq_save_reads: typing.Optional[bool], krakenuniq_save_readclassifications: typing.Optional[bool], run_bracken: typing.Optional[bool], run_malt: typing.Optional[bool], malt_save_reads: typing.Optional[bool], malt_generate_megansummary: typing.Optional[bool], run_metaphlan: typing.Optional[bool], run_motus: typing.Optional[bool], motus_use_relative_abundance: typing.Optional[bool], motus_save_mgc_read_counts: typing.Optional[bool], motus_remove_ncbi_ids: typing.Optional[bool], run_kmcp: typing.Optional[bool], kmcp_save_search: typing.Optional[bool], run_ganon: typing.Optional[bool], ganon_save_readclassifications: typing.Optional[bool], ganon_report_rank: typing.Optional[str], run_profile_standardisation: typing.Optional[bool], standardisation_motus_generatebiom: typing.Optional[bool], run_krona: typing.Optional[bool], krona_taxonomy_directory: typing.Optional[str], taxpasta_taxonomy_dir: typing.Optional[str], taxpasta_add_name: typing.Optional[bool], taxpasta_add_rank: typing.Optional[bool], taxpasta_add_lineage: typing.Optional[bool], taxpasta_add_idlineage: typing.Optional[bool], taxpasta_add_ranklineage: typing.Optional[bool], taxpasta_ignore_errors: typing.Optional[bool], multiqc_methods_description: typing.Optional[str], preprocessing_qc_tool: typing.Optional[str] = 'fastqc', shortread_qc_tool: typing.Optional[str] = 'fastp', shortread_qc_minlength: typing.Optional[int] = 15, shortread_complexityfilter_tool: typing.Optional[str] = 'bbduk', shortread_complexityfilter_entropy: typing.Optional[float] = 0.3, shortread_complexityfilter_bbduk_windowsize: typing.Optional[int] = 50, shortread_complexityfilter_fastp_threshold: typing.Optional[int] = 30, shortread_complexityfilter_prinseqplusplus_mode: typing.Optional[str] = 'entropy', shortread_complexityfilter_prinseqplusplus_dustscore: typing.Optional[float] = 0.5, longread_qc_qualityfilter_minlength: typing.Optional[int] = 1000, longread_qc_qualityfilter_keeppercent: typing.Optional[int] = 90, longread_qc_qualityfilter_targetbases: typing.Optional[int] = 500000000, diamond_output_format: typing.Optional[str] = 'tsv', kaiju_taxon_rank: typing.Optional[str] = 'species', krakenuniq_ram_chunk_size: typing.Optional[str] = '16G', krakenuniq_batch_size: typing.Optional[int] = 20, malt_mode: typing.Optional[str] = 'BlastN', kmcp_mode: typing.Optional[int] = 3, ganon_report_type: typing.Optional[str] = 'reads', ganon_report_toppercentile: typing.Optional[int] = 0, ganon_report_mincount: typing.Optional[int] = 0, ganon_report_maxcount: typing.Optional[int] = 0, standardisation_taxpasta_format: typing.Optional[str] = 'tsv') -> None:
    """
    nf-core/taxprofiler

    Sample Description
    """

    pvc_name: str = initialize()
    nextflow_runtime(pvc_name=pvc_name, input=input, databases=databases, save_untarred_databases=save_untarred_databases, outdir=outdir, email=email, multiqc_title=multiqc_title, skip_preprocessing_qc=skip_preprocessing_qc, preprocessing_qc_tool=preprocessing_qc_tool, save_preprocessed_reads=save_preprocessed_reads, save_analysis_ready_fastqs=save_analysis_ready_fastqs, perform_shortread_qc=perform_shortread_qc, shortread_qc_tool=shortread_qc_tool, shortread_qc_skipadaptertrim=shortread_qc_skipadaptertrim, shortread_qc_adapter1=shortread_qc_adapter1, shortread_qc_adapter2=shortread_qc_adapter2, shortread_qc_adapterlist=shortread_qc_adapterlist, shortread_qc_mergepairs=shortread_qc_mergepairs, shortread_qc_includeunmerged=shortread_qc_includeunmerged, shortread_qc_minlength=shortread_qc_minlength, shortread_qc_dedup=shortread_qc_dedup, perform_shortread_complexityfilter=perform_shortread_complexityfilter, shortread_complexityfilter_tool=shortread_complexityfilter_tool, shortread_complexityfilter_entropy=shortread_complexityfilter_entropy, shortread_complexityfilter_bbduk_windowsize=shortread_complexityfilter_bbduk_windowsize, shortread_complexityfilter_bbduk_mask=shortread_complexityfilter_bbduk_mask, shortread_complexityfilter_fastp_threshold=shortread_complexityfilter_fastp_threshold, shortread_complexityfilter_prinseqplusplus_mode=shortread_complexityfilter_prinseqplusplus_mode, shortread_complexityfilter_prinseqplusplus_dustscore=shortread_complexityfilter_prinseqplusplus_dustscore, save_complexityfiltered_reads=save_complexityfiltered_reads, perform_longread_qc=perform_longread_qc, longread_qc_skipadaptertrim=longread_qc_skipadaptertrim, longread_qc_skipqualityfilter=longread_qc_skipqualityfilter, longread_qc_qualityfilter_minlength=longread_qc_qualityfilter_minlength, longread_qc_qualityfilter_keeppercent=longread_qc_qualityfilter_keeppercent, longread_qc_qualityfilter_targetbases=longread_qc_qualityfilter_targetbases, perform_shortread_hostremoval=perform_shortread_hostremoval, perform_longread_hostremoval=perform_longread_hostremoval, hostremoval_reference=hostremoval_reference, shortread_hostremoval_index=shortread_hostremoval_index, longread_hostremoval_index=longread_hostremoval_index, save_hostremoval_index=save_hostremoval_index, save_hostremoval_bam=save_hostremoval_bam, save_hostremoval_unmapped=save_hostremoval_unmapped, perform_runmerging=perform_runmerging, save_runmerged_reads=save_runmerged_reads, run_centrifuge=run_centrifuge, centrifuge_save_reads=centrifuge_save_reads, run_diamond=run_diamond, diamond_output_format=diamond_output_format, diamond_save_reads=diamond_save_reads, run_kaiju=run_kaiju, kaiju_expand_viruses=kaiju_expand_viruses, kaiju_taxon_rank=kaiju_taxon_rank, run_kraken2=run_kraken2, kraken2_save_reads=kraken2_save_reads, kraken2_save_readclassifications=kraken2_save_readclassifications, kraken2_save_minimizers=kraken2_save_minimizers, run_krakenuniq=run_krakenuniq, krakenuniq_save_reads=krakenuniq_save_reads, krakenuniq_ram_chunk_size=krakenuniq_ram_chunk_size, krakenuniq_save_readclassifications=krakenuniq_save_readclassifications, krakenuniq_batch_size=krakenuniq_batch_size, run_bracken=run_bracken, run_malt=run_malt, malt_mode=malt_mode, malt_save_reads=malt_save_reads, malt_generate_megansummary=malt_generate_megansummary, run_metaphlan=run_metaphlan, run_motus=run_motus, motus_use_relative_abundance=motus_use_relative_abundance, motus_save_mgc_read_counts=motus_save_mgc_read_counts, motus_remove_ncbi_ids=motus_remove_ncbi_ids, run_kmcp=run_kmcp, kmcp_mode=kmcp_mode, kmcp_save_search=kmcp_save_search, run_ganon=run_ganon, ganon_save_readclassifications=ganon_save_readclassifications, ganon_report_type=ganon_report_type, ganon_report_rank=ganon_report_rank, ganon_report_toppercentile=ganon_report_toppercentile, ganon_report_mincount=ganon_report_mincount, ganon_report_maxcount=ganon_report_maxcount, run_profile_standardisation=run_profile_standardisation, standardisation_motus_generatebiom=standardisation_motus_generatebiom, run_krona=run_krona, krona_taxonomy_directory=krona_taxonomy_directory, standardisation_taxpasta_format=standardisation_taxpasta_format, taxpasta_taxonomy_dir=taxpasta_taxonomy_dir, taxpasta_add_name=taxpasta_add_name, taxpasta_add_rank=taxpasta_add_rank, taxpasta_add_lineage=taxpasta_add_lineage, taxpasta_add_idlineage=taxpasta_add_idlineage, taxpasta_add_ranklineage=taxpasta_add_ranklineage, taxpasta_ignore_errors=taxpasta_ignore_errors, multiqc_methods_description=multiqc_methods_description)

