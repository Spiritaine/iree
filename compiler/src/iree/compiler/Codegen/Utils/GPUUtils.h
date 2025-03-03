// Copyright 2021 The IREE Authors
//
// Licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

#ifndef IREE_COMPILER_CODEGEN_UTILS_GPUUTILS_H_
#define IREE_COMPILER_CODEGEN_UTILS_GPUUTILS_H_

#include "iree/compiler/Codegen/Utils/Utils.h"
#include "mlir/Dialect/MemRef/IR/MemRef.h"
#include "mlir/Dialect/Vector/IR/VectorOps.h"
namespace mlir {
namespace iree_compiler {

static constexpr int32_t kNumGPUDims = 3;
static constexpr int32_t kWarpSize = 32;

//===----------------------------------------------------------------------===//
// GPU processor IDs and sizes
//===----------------------------------------------------------------------===//

llvm::SmallVector<linalg::ProcInfo, 2> getGPUThreadIdsAndCounts(
    OpBuilder &builder, Location loc, unsigned numDims,
    llvm::ArrayRef<int64_t> workgroupSize);

/// Computes subgroup ID and returns in (X, Y, Z) order.
///
/// Note that CUDA doesn't have a subgroupId equivalent so we are are computing
/// the subgroup ID based on the threadID. When tiling to warp we assume each
/// warp is full and we pick a workgroup size so that `workgroupSize.x %
/// warpSize == 0`. This is why we can have warpId = { threadId.x / warpSize,
/// threadId.y, threadId.z }.
llvm::SmallVector<linalg::ProcInfo, 2> getSubgroupIdsAndCounts(
    OpBuilder &builder, Location loc, unsigned warpSize, unsigned numDims,
    llvm::ArrayRef<int64_t> numSubgroups);

/// Returns the workgroup size associated to the funcOp entry point.
std::array<int64_t, 3> getWorkgroupSize(func::FuncOp funcOp);

//===----------------------------------------------------------------------===//
// GPU vectorization
//===----------------------------------------------------------------------===//

/// Returns true if we can use all threads to perform vectorized load/store of
/// the given `shape`.
bool canPerformVectorAccessUsingAllThreads(ArrayRef<int64_t> shape,
                                           int64_t threadCount,
                                           int64_t vectorSize);

/// Pick an unrolling order that will allow tensorcore operation to reuse LHS
/// register. This is needed to get good performance on sm_80 target.
Optional<SmallVector<int64_t>> gpuMmaUnrollOrder(
    vector::ContractionOp contract);

//===----------------------------------------------------------------------===//
// GPU workgroup memory
//===----------------------------------------------------------------------===//

/// Allocates GPU workgroup memory matching the given `subview`. If there are
/// dynamic dimensions, the bounds are in `sizeBounds`.
Optional<Value> allocateWorkgroupMemory(OpBuilder &builder,
                                        memref::SubViewOp subview,
                                        ArrayRef<Value> sizeBounds,
                                        DataLayout &);

/// Deallocates GPU workgroup memory behind `buffer`.
LogicalResult deallocateWorkgroupMemory(OpBuilder &, Value buffer);

/// Copies `src` value to `dst` in shared memory.
LogicalResult copyToWorkgroupMemory(OpBuilder &builder, Value src, Value dst);

/// Propagates shared memory copy to producer linalg.fill or consumer
/// linalg.generic when possible.
void propagateSharedMemoryCopy(func::FuncOp funcOp);

/// Inserts barriers before and after shared memory copy.
void insertBarriersAroundSharedMemoryCopy(func::FuncOp funcOp);

/// Emit reduction across a group for a given input.
Value emitGPUGroupReduction(Location loc, OpBuilder &builder, Value input,
                            vector::CombiningKind kind, uint32_t size,
                            const int warpSize);

/// Return the native size of an operation used in contraction calculation.
// TODO: Make this take HW specific sizes.
Optional<SmallVector<int64_t>> getWmmaNativeVectorSize(Operation *op);

}  // namespace iree_compiler
}  // namespace mlir

#endif  // IREE_COMPILER_CODEGEN_UTILS_GPUUTILS_H_
