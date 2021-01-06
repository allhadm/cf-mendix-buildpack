import logging


def stage(buildpack_path, build_path, cache_dir):
    logging.info(
        "buildpackpath is %s" "build path is %s " "cache_dir path is %s",
        buildpack_path,
        build_path,
        cache_dir,
    )


def run():
    logging.info("###################### running met sidecar ###############")
