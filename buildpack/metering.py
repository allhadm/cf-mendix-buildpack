import logging
import shutil
import os
import subprocess


METERING_SIDECAR_DIR = os.path.abspath("/home/vcap/app/metering")


def stage(buildpack_path, build_path, cache_dir):
    logging.info(
        "buildpackpath is %s" "build path is %s " "cache_dir path is %s",
        buildpack_path,
        build_path,
        cache_dir,
    )
    shutil.copytree(
        os.path.join(buildpack_path, "etc/metering"),
        os.path.join(build_path, "metering"),
    )


def run():
    logging.info("###################### running met sidecar ###############")
    subprocess.Popen(METERING_SIDECAR_DIR + "/metering")
