__all__ = ["CONFIG_SCHEMA"]

import yaml

CONFIG_SCHEMA = yaml.safe_load(
    """
$schema: http://json-schema.org/draft-07/schema#
$id: https://github.com/lsst-ts/ts_salobjATHexapod/blob/master/schema/ATHexapod.yaml
title: ATHexapod v2
description: Schema for ATHexapod configuration files
type: object
properties:
    limit_xy_max:
        description: The max limits of the xy axii. mm
        type: number
    limit_z_min:
        description: The min limits of the z axis. mm
        type: number
    limit_z_max:
        description: The max limits of the z axis. mm
        type: number
    limit_uv_max:
        description: The max limits of the UV axii. degree
        type: number
    limit_w_min:
        description: The min limit of the W axis. degree
        type: number
    limit_w_max:
        description: The max limit of the W axis. degree
        type: number
    pivot_x:
        description: Pivot position. mm
        type: number
    pivot_y:
        description: Pivot position. mm
        type: number
    pivot_z:
        description: Pivot position. mm
        type: number
    speed:
        description: The speed. mm/s
        type: number
    auto_reference:
        description: >-
            Should the CSC attempt to auto-reference the hexapod when enabling?
            If True, will check if axis is referenced and perform reference if not.
        type: boolean
    host:
        description: >-
            The ip address or host name of the hexapod controller or simulator.
            It is also possible to use an environment variable as the host IP.
            To enable this mode set host to start with "ENV." followed by the environment
            variable name. For instance, to use ATHEXAPOD_HOST environment variable,
            the configuration must be "ENV.ATHEXAPOD_HOST".
        type: string
    port:
        description: The port of the tcp connection to the controller or simulator.
        type: integer
        minimum: 0
        maximum: 65535
    connection_timeout:
        description: The amount of time to wait for timeout of the connection. Seconds.
        type: number
    reference_timeout:
        description: How long to wait for a reference activity before timing out. Seconds.
        type: number
    movement_timeout:
        description: How long to wait for a movement command before timing out. Seconds.
        type: number
    max_length:
        description: The maximum number of bytes a message can be. Bytes.
        type: integer
"""
)
