ARG deploy_env_tag=salobj_5.15.2

FROM lsstts/deploy-env:${deploy_env_tag}

ARG idl_conda_version=1.1.1_v4.7.0
ARG athexapod_conda_version=1.1.0
ARG athexapod_config_branch=master

RUN mkdir /home/saluser/repos

WORKDIR /home/saluser/repos

RUN git clone https://github.com/lsst-ts/ts_config_attcs.git

ENV TS_CONFIG_ATTCS_DIR=/home/saluser/repos/ts_config_attcs
ENV CSC_INDEX=1
ENV CSC_MODE=0

WORKDIR /home/saluser/repos/ts_config_attcs

RUN git fetch --all && git checkout ${attcs_config_branch}

RUN source ~/miniconda3/bin/activate && \
    source $OSPL_HOME/release.com && \
    conda install -c lsstts ts-idl=${idl_conda_version} && \
    conda install -c lsstts ts-athexapod=${athexapod_conda_version}

COPY setup.sh /home/saluser/.setup.sh

USER saluser

WORKDIR /home/saluser/
