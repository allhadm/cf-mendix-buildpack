import logging
import os
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


def _set_up_environment():
    e = dict(os.environ.copy())
    if "MXRUNTIME_License.SubscriptionSecret" in os.environ:
        logging.info("Setting MXUMS_SUBSCRIPTION_SECRET")
        e["MXUMS_SUBSCRIPTION_SECRET"] = os.environ[
            "MXRUNTIME_License.SubscriptionSecret"
        ]
        #os.environ.pop("MXRUNTIME_License.SubscriptionSecret")
        del os.environ['MXRUNTIME_License.SubscriptionSecret']
        #os.unsetenv("MXRUNTIME_License.SubscriptionSecret")
    if "MXRUNTIME_License.LicenseServerURL" in os.environ:
        logging.info(
            "Setting MXUMS_LICENSESERVER_URL to {%s}",
            os.environ["MXRUNTIME_License.LicenseServerURL"],
        )
        e["MXUMS_LICENSESERVER_URL"] = os.environ[
            "MXRUNTIME_License.LicenseServerURL"
        ]
        #os.environ.pop("MXRUNTIME_License.LicenseServerURL")
        os.unsetenv("MXRUNTIME_License.LicenseServerURL")
    if "MXRUNTIME_License.EnvironmentName" in os.environ:
        logging.info("Setting MXUMS_ENVIRONMENT_NAME")
        e["MXUMS_ENVIRONMENT_NAME"] = os.environ[
            "MXRUNTIME_License.EnvironmentName"
        ]
        os.environ.pop("MXRUNTIME_License.EnvironmentName")
    dbconfig = database.get_config()
    if dbconfig:
        os.environ["DD_SERVICE_MAPPING"] = "postgres://{}:{}@{}/{}".format(
            dbconfig["DatabaseUserName"],
            dbconfig["DatabasePassword"],
            dbconfig["DatabaseHost"],
            dbconfig["DatabaseName"],
        )
    logging.info(dbconfig)
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
    else:
        logging.info("Usage metering is NOT enabled")


def run(m2ee):
    logging.info("################## running met sidecar ###############")
    logging.info(m2ee)
    subprocess.Popen(
        SIDECAR_DIR + "/" + SIDECAR_FILENAME, env=_set_up_environment()
    )
