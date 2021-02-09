import logging
import os
import json
import subprocess


from buildpack import util
from buildpack.runtime_components import database

NAMESPACE = "metering"
SIDECAR_VERSION = "v0.0.1"
SIDECAR_ARCHIVE = "metering-sidecar-linux-amd64-{}.tar.gz".format(
    SIDECAR_VERSION
)
SIDECAR_URL_ROOT = "/mx-buildpack/experimental{}".format(NAMESPACE)
SIDECAR_DIR = os.path.abspath("/home/vcap/app/metering")
SIDECAR_FILENAME = "cf-metering-sidecar"


def _download(build_path, cache_dir):
    util.download_and_unpack(
        "https://mx-cdn-test2.s3-eu-west-1.amazonaws.com/mx-buildpack/experimental/metering/metering-sidecar-linux-amd64-v0.0.1.tar.gz",
        os.path.join(build_path, NAMESPACE),
        cache_dir=cache_dir,
    )
    logging.info(
        "Downloaded <%s> to <%s>",
        "https://mx-cdn-test2.s3-eu-west-1.amazonaws.com/mx-buildpack/experimental/metering/metering-sidecar-linux-amd64-v0.0.1.tar.gz",
        os.path.join(build_path, NAMESPACE),
    )
    logging.info(
        "/tmp/app/metering/cf-metering-sidecar exists <%s>?",
        os.path.isfile("/tmp/app/metering/cf-metering-sidecar"),
    )


def _is_usage_metering_enabled():
    if (
        "MXUMS_LICENSESERVER_URL" in os.environ
        or "MXRUNTIME_License.LicenseServerURL" in os.environ
    ):
        return True


def _get_project_id(file_path):
    try:
        with open(file_path) as file_handle:
            data = json.loads(file_handle.read())
            return data["ProjectID"]
    except IOError:
        raise Exception("No model/metadata.json")


def write_file(output_file_path, content):
    if output_file_path is None:
        print(content)
    else:
        try:
            with open(output_file_path, "w") as f:
                json.dump(content, f)
        except Exception as exception:
            raise Exception(
                "Error while trying to write the configuration to a file. Reason: '{}'".format(
                    exception
                )
            )


def _set_up_environment():
    if "MXRUNTIME_License.SubscriptionSecret" in os.environ:
        logging.info("Setting MXUMS_SUBSCRIPTION_SECRET")
        os.environ["MXUMS_SUBSCRIPTION_SECRET"] = os.environ[
            "MXRUNTIME_License.SubscriptionSecret"
        ]
    if "MXRUNTIME_License.LicenseServerURL" in os.environ:
        logging.info(
            "Setting MXUMS_LICENSESERVER_URL to {%s}",
            os.environ["MXRUNTIME_License.LicenseServerURL"],
        )
        os.environ["MXUMS_LICENSESERVER_URL"] = os.environ[
            "MXRUNTIME_License.LicenseServerURL"
        ]
    if "MXRUNTIME_License.EnvironmentName" in os.environ:
        logging.info("Setting MXUMS_ENVIRONMENT_NAME")
        os.environ["MXUMS_ENVIRONMENT_NAME"] = os.environ[
            "MXRUNTIME_License.EnvironmentName"
        ]
    dbconfig = database.get_config()
    if dbconfig:
        os.environ[
            "MXUMS_DB_CONNECTION_URL"
        ] = "postgres://{}:{}@{}/{}".format(
            dbconfig["DatabaseUserName"],
            dbconfig["DatabasePassword"],
            dbconfig["DatabaseHost"],
            dbconfig["DatabaseName"],
        )
    project_id = _get_project_id(SIDECAR_DIR + "/conf.json")
    os.environ["MXUMS_PROJECT_ID"] = project_id
    e = dict(os.environ.copy())
    return e


def stage(buildpack_path, build_path, cache_dir):
    logging.info(
        "buildpackpath is <%s>" "build path is <%s> " "cache_dir path is <%s>",
        buildpack_path,
        build_path,
        cache_dir,
    )
    if _is_usage_metering_enabled():
        logging.info("Usage metering is enabled")
        _download(build_path, cache_dir)

        project_id = _get_project_id(
            os.path.join(build_path, "model", "metadata.json")
        )

        config = {"ProjectID": project_id}
        logging.info(config)

        logging.debug("Writing nginx configuration file...")
        write_file(os.path.join(build_path, NAMESPACE) + "/conf.json", config)

    else:
        logging.info("Usage metering is NOT enabled")


def run():
    logging.info("################## running met sidecar ###############")
    if _is_usage_metering_enabled():
        subprocess.Popen(
            SIDECAR_DIR + "/" + SIDECAR_FILENAME, env=_set_up_environment()
        )
