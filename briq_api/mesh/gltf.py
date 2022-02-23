from typing import List, Tuple
import numpy as np
import pygltflib

from dataclasses import dataclass


@dataclass
class Material:
    name: str
    color: str  # as "#ffaa00"


@dataclass
class Primitive:
    points: List[Tuple[float, float, float]]
    triangles: List[Tuple[int, int, int]]
    material: Material


def to_gltf(prims: List[Primitive]):
    primitives = []
    accessors = []
    bufferViews = []
    materials = []

    blobs = b""
    totalBufferOffset = 0

    for (i, primitive) in enumerate(prims):

        rgbaCol = [int(primitive.material.color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        materials.append(pygltflib.Material(
            name=primitive.material.name,
            pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(baseColorFactor=rgbaCol + [1]),
            alphaCutoff=None,
        ))

        points = np.array(primitive.points, dtype="float32")
        triangles = np.array(primitive.triangles, dtype="uint16")
        triangles_binary_blob = triangles.flatten().tobytes()
        points_binary_blob = points.tobytes()
        primitives.append(pygltflib.Primitive(
            attributes=pygltflib.Attributes(POSITION=i * 2 + 1),
            indices=i * 2,
            material=i
        ))
        accessors.append(pygltflib.Accessor(
            bufferView=i * 2,
            componentType=pygltflib.UNSIGNED_SHORT,
            count=triangles.size,
            type=pygltflib.SCALAR,
            max=[int(triangles.max())],
            min=[int(triangles.min())],
        ))
        accessors.append(pygltflib.Accessor(
            bufferView=i * 2 + 1,
            componentType=pygltflib.FLOAT,
            count=len(points),
            type=pygltflib.VEC3,
            max=points.max(axis=0).tolist(),
            min=points.min(axis=0).tolist(),
        ))
        bufferViews.append(pygltflib.BufferView(
            buffer=0,
            byteOffset=totalBufferOffset,
            byteLength=len(triangles_binary_blob),
            target=pygltflib.ELEMENT_ARRAY_BUFFER,
        ))
        totalBufferOffset += len(triangles_binary_blob)
        bufferViews.append(pygltflib.BufferView(
            buffer=0,
            byteOffset=totalBufferOffset,
            byteLength=len(points_binary_blob),
            target=pygltflib.ARRAY_BUFFER,
        ))
        totalBufferOffset += len(points_binary_blob)
        blobs += triangles_binary_blob + points_binary_blob

    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0])],
        nodes=[pygltflib.Node(mesh=0)],
        meshes=[pygltflib.Mesh(primitives=primitives)],
        materials=materials,
        accessors=accessors,
        bufferViews=bufferViews,
        buffers=[
            pygltflib.Buffer(
                byteLength=totalBufferOffset
            )
        ],
    )
    gltf.set_binary_blob(blobs)
    return gltf