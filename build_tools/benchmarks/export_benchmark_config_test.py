#!/usr/bin/env python3
# Copyright 2022 The IREE Authors
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import unittest

from e2e_test_framework.definitions import common_definitions, iree_definitions
import export_benchmark_config

COMMON_MODEL = common_definitions.Model(
    id="tflite",
    name="model_tflite",
    tags=[],
    source_type=common_definitions.ModelSourceType.EXPORTED_TFLITE,
    source_url="",
    entry_function="predict",
    input_types=["1xf32"])
COMMON_GEN_CONFIG = iree_definitions.ModuleGenerationConfig(
    imported_model=iree_definitions.ImportedModel.from_model(COMMON_MODEL),
    compile_config=iree_definitions.CompileConfig(id="1",
                                                  tags=[],
                                                  compile_targets=[]))
COMMON_EXEC_CONFIG = iree_definitions.ModuleExecutionConfig(
    id="exec",
    tags=[],
    loader=iree_definitions.RuntimeLoader.EMBEDDED_ELF,
    driver=iree_definitions.RuntimeDriver.LOCAL_SYNC)


class ExportBenchmarkConfigTest(unittest.TestCase):

  def test_filter_and_group_run_configs_set_all_filters(self):
    device_spec_a = common_definitions.DeviceSpec(
        id="dev_a_cpu",
        device_name="dev_a_cpu",
        architecture=common_definitions.DeviceArchitecture.RV64_GENERIC,
        host_environment=common_definitions.HostEnvironment.ANDROID_ARMV8_2_A)
    device_spec_b = common_definitions.DeviceSpec(
        id="dev_a_gpu",
        device_name="dev_a_gpu",
        architecture=common_definitions.DeviceArchitecture.VALHALL_MALI,
        host_environment=common_definitions.HostEnvironment.ANDROID_ARMV8_2_A)
    device_spec_c = common_definitions.DeviceSpec(
        id="dev_c",
        device_name="dev_c",
        architecture=common_definitions.DeviceArchitecture.CUDA_SM80,
        host_environment=common_definitions.HostEnvironment.LINUX_X86_64)
    matched_run_config_a = iree_definitions.E2EModelRunConfig(
        module_generation_config=COMMON_GEN_CONFIG,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_a,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)
    unmatched_run_config_b = iree_definitions.E2EModelRunConfig(
        module_generation_config=COMMON_GEN_CONFIG,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_b,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)
    matched_run_config_c = iree_definitions.E2EModelRunConfig(
        module_generation_config=COMMON_GEN_CONFIG,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_c,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)
    matchers = [(lambda config: config.target_device_spec.architecture.
                 architecture == "cuda"),
                (lambda config: config.target_device_spec.host_environment.
                 platform == "android")]

    run_config_map = export_benchmark_config.filter_and_group_run_configs(
        run_configs=[
            matched_run_config_a, unmatched_run_config_b, matched_run_config_c
        ],
        target_device_names={"dev_a_cpu", "dev_c"},
        preset_matchers=matchers)

    self.assertEqual(run_config_map, {
        "dev_a_cpu": [matched_run_config_a],
        "dev_c": [matched_run_config_c],
    })

  def test_filter_and_group_run_configs_include_all(self):
    device_spec_a = common_definitions.DeviceSpec(
        id="dev_a_cpu",
        device_name="dev_a_cpu",
        architecture=common_definitions.DeviceArchitecture.RV64_GENERIC,
        host_environment=common_definitions.HostEnvironment.ANDROID_ARMV8_2_A)
    device_spec_b = common_definitions.DeviceSpec(
        id="dev_a_gpu",
        device_name="dev_a_gpu",
        architecture=common_definitions.DeviceArchitecture.VALHALL_MALI,
        host_environment=common_definitions.HostEnvironment.ANDROID_ARMV8_2_A)
    device_spec_c = common_definitions.DeviceSpec(
        id="dev_a_second_gpu",
        device_name="dev_a_gpu",
        architecture=common_definitions.DeviceArchitecture.ADRENO_GENERIC,
        host_environment=common_definitions.HostEnvironment.ANDROID_ARMV8_2_A)
    run_config_a = iree_definitions.E2EModelRunConfig(
        module_generation_config=COMMON_GEN_CONFIG,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_a,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)
    run_config_b = iree_definitions.E2EModelRunConfig(
        module_generation_config=COMMON_GEN_CONFIG,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_b,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)
    run_config_c = iree_definitions.E2EModelRunConfig(
        module_generation_config=COMMON_GEN_CONFIG,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_c,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)

    run_config_map = export_benchmark_config.filter_and_group_run_configs(
        run_configs=[run_config_a, run_config_b, run_config_c])

    self.maxDiff = 100000

    self.assertEqual(run_config_map, {
        "dev_a_cpu": [run_config_a],
        "dev_a_gpu": [run_config_b, run_config_c],
    })

  def test_filter_and_group_run_configs_set_target_device_names(self):
    device_spec_a = common_definitions.DeviceSpec(
        id="dev_a",
        device_name="dev_a",
        architecture=common_definitions.DeviceArchitecture.RV64_GENERIC,
        host_environment=common_definitions.HostEnvironment.ANDROID_ARMV8_2_A)
    device_spec_b = common_definitions.DeviceSpec(
        id="dev_b",
        device_name="dev_b",
        architecture=common_definitions.DeviceArchitecture.VALHALL_MALI,
        host_environment=common_definitions.HostEnvironment.ANDROID_ARMV8_2_A)
    run_config_a = iree_definitions.E2EModelRunConfig(
        module_generation_config=COMMON_GEN_CONFIG,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_a,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)
    run_config_b = iree_definitions.E2EModelRunConfig(
        module_generation_config=COMMON_GEN_CONFIG,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_b,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)

    run_config_map = export_benchmark_config.filter_and_group_run_configs(
        run_configs=[run_config_a, run_config_b],
        target_device_names={"dev_a", "dev_b"})

    self.assertEqual(run_config_map, {
        "dev_a": [run_config_a],
        "dev_b": [run_config_b],
    })

  def test_filter_and_group_run_configs_set_preset_matchers(self):
    small_model = common_definitions.Model(
        id="small_model",
        name="small_model",
        tags=[],
        source_type=common_definitions.ModelSourceType.EXPORTED_TFLITE,
        source_url="",
        entry_function="predict",
        input_types=["1xf32"])
    big_model = common_definitions.Model(
        id="big_model",
        name="big_model",
        tags=[],
        source_type=common_definitions.ModelSourceType.EXPORTED_TFLITE,
        source_url="",
        entry_function="predict",
        input_types=["1xf32"])
    compile_config = iree_definitions.CompileConfig(id="1",
                                                    tags=[],
                                                    compile_targets=[])
    small_gen_config = iree_definitions.ModuleGenerationConfig(
        imported_model=iree_definitions.ImportedModel.from_model(small_model),
        compile_config=compile_config)
    big_gen_config = iree_definitions.ModuleGenerationConfig(
        imported_model=iree_definitions.ImportedModel.from_model(big_model),
        compile_config=compile_config)
    device_spec_a = common_definitions.DeviceSpec(
        id="dev_a",
        device_name="dev_a",
        architecture=common_definitions.DeviceArchitecture.RV64_GENERIC,
        host_environment=common_definitions.HostEnvironment.ANDROID_ARMV8_2_A)
    device_spec_b = common_definitions.DeviceSpec(
        id="dev_b",
        device_name="dev_b",
        architecture=common_definitions.DeviceArchitecture.VALHALL_MALI,
        host_environment=common_definitions.HostEnvironment.ANDROID_ARMV8_2_A)
    run_config_a = iree_definitions.E2EModelRunConfig(
        module_generation_config=small_gen_config,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_a,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)
    run_config_b = iree_definitions.E2EModelRunConfig(
        module_generation_config=big_gen_config,
        module_execution_config=COMMON_EXEC_CONFIG,
        target_device_spec=device_spec_b,
        input_data=common_definitions.ZEROS_MODEL_INPUT_DATA)

    run_config_map = export_benchmark_config.filter_and_group_run_configs(
        run_configs=[run_config_a, run_config_b],
        preset_matchers=[
            lambda config: config.module_generation_config.imported_model.model.
            id == "small_model"
        ])

    self.assertEqual(run_config_map, {
        "dev_a": [run_config_a],
    })


if __name__ == "__main__":
  unittest.main()
