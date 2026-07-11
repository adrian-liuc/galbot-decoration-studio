import { useEffect, useRef, useState } from 'react'
import { Canvas, type ThreeEvent } from '@react-three/fiber'
import { OrbitControls, TransformControls } from '@react-three/drei'
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import URDFLoader from 'urdf-loader'
import type { URDFRobot } from 'urdf-loader'
import type { MountPointInfo, QuaternionXYZW, Vec3 } from '../types'
import { BODY_COLOR_GROUPS } from '../bodyColorGroups'

// Decoration geometry from the backend is generated in millimeters (the
// natural unit for 3D printing); the robot URDF is authored in meters, so
// decorations need a 1/1000 scale to sit correctly on the robot model.
const MM_TO_M = 0.001

function useURDFRobot(urdfUrl: string, basePath: string) {
  const [robot, setRobot] = useState<URDFRobot | null>(null)

  useEffect(() => {
    let cancelled = false
    const manager = new THREE.LoadingManager()
    const loader = new URDFLoader(manager)
    loader.workingPath = basePath
    loader.parseVisual = true
    loader.parseCollision = false
    loader.loadMeshCb = (path, meshManager, _material, onComplete) => {
      new GLTFLoader(meshManager).load(
        path,
        (gltf) => onComplete(gltf.scene),
        undefined,
        (err) => onComplete(null as unknown as THREE.Object3D, err as Error),
      )
    }
    loader.load(urdfUrl, (loadedRobot) => {
      if (cancelled) return
      loadedRobot.rotation.x = -Math.PI / 2
      setRobot(loadedRobot)
    })
    return () => {
      cancelled = true
    }
  }, [urdfUrl, basePath])

  return robot
}

/** Loads a decoration mesh and attaches it as a child of its mount link. Used
 * for both confirmed (static) placements and the one editable draft. */
function useAttachedGroup(
  robot: URDFRobot | null,
  decorationUrl: string | null,
  mountInfo: MountPointInfo | undefined,
  offset: Vec3,
  rotation: QuaternionXYZW,
) {
  const [group, setGroup] = useState<THREE.Group | null>(null)
  const attachedGroupRef = useRef<THREE.Group | null>(null)

  useEffect(() => {
    if (!robot || !decorationUrl || !mountInfo) return
    const link = robot.links[mountInfo.link]
    if (!link) return

    let cancelled = false
    new GLTFLoader().load(decorationUrl, (gltf) => {
      if (cancelled) return
      if (attachedGroupRef.current) {
        attachedGroupRef.current.parent?.remove(attachedGroupRef.current)
      }
      const newGroup = new THREE.Group()
      newGroup.position.set(...offset)
      newGroup.quaternion.set(...rotation)
      newGroup.scale.set(MM_TO_M, MM_TO_M, MM_TO_M)
      newGroup.add(gltf.scene)
      link.add(newGroup)
      attachedGroupRef.current = newGroup
      setGroup(newGroup)
    })

    return () => {
      cancelled = true
      if (attachedGroupRef.current) {
        attachedGroupRef.current.parent?.remove(attachedGroupRef.current)
        attachedGroupRef.current = null
        setGroup(null)
      }
    }
    // offset/rotation intentionally excluded: dragging shouldn't reload the mesh.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [robot, decorationUrl, mountInfo])

  // Reposition the existing group (without reloading the mesh) when the
  // caller-provided offset/rotation changes externally (e.g. loading a saved
  // design, or a surface-snap click).
  useEffect(() => {
    attachedGroupRef.current?.position.set(...offset)
    attachedGroupRef.current?.quaternion.set(...rotation)
  }, [offset, rotation])

  return group
}

// three.js multiplies a MeshStandardMaterial's texture color by
// `material.color`, so setting a tint here recolors the part while keeping
// its baked-in shading/texture detail — the same "team color" tint trick
// used by most 3D configurators, instead of flattening to a solid color.
function useBodyColors(robot: URDFRobot | null, bodyColors: Record<string, string>) {
  useEffect(() => {
    if (!robot) return
    for (const group of BODY_COLOR_GROUPS) {
      const hex = bodyColors[group.id]
      if (!hex) continue
      const color = new THREE.Color(hex)
      for (const [linkName, link] of Object.entries(robot.links)) {
        if (!group.linkPrefixes.some((prefix) => linkName.startsWith(prefix))) continue
        link.traverse((obj) => {
          if (!(obj instanceof THREE.Mesh)) return
          const materials = Array.isArray(obj.material) ? obj.material : [obj.material]
          for (const material of materials) {
            if (material && 'color' in material) {
              ;(material as THREE.MeshStandardMaterial).color.set(color)
            }
          }
        })
      }
    }
  }, [robot, bodyColors])
}

export interface ConfirmedPlacementView {
  key: string
  mountPoint: string
  previewUrl: string
  offset: Vec3
  rotation: QuaternionXYZW
}

function ConfirmedDecoration({
  robot,
  mountPoints,
  placement,
}: {
  robot: URDFRobot
  mountPoints: Record<string, MountPointInfo>
  placement: ConfirmedPlacementView
}) {
  useAttachedGroup(robot, placement.previewUrl, mountPoints[placement.mountPoint], placement.offset, placement.rotation)
  return null
}

interface DraftDecorationProps {
  robot: URDFRobot
  mountInfo: MountPointInfo | undefined
  decorationUrl: string | null
  offset: Vec3
  rotation: QuaternionXYZW
  onOffsetChange: (offset: Vec3) => void
  onRotationChange: (rotation: QuaternionXYZW) => void
  transformMode: 'translate' | 'rotate'
  orbitRef: React.RefObject<OrbitControlsImpl | null>
}

function DraftDecoration({
  robot,
  mountInfo,
  decorationUrl,
  offset,
  rotation,
  onOffsetChange,
  onRotationChange,
  transformMode,
  orbitRef,
}: DraftDecorationProps) {
  const group = useAttachedGroup(robot, decorationUrl, mountInfo, offset, rotation)
  if (!group) return null
  return (
    <TransformControls
      key={group.uuid}
      object={group}
      mode={transformMode}
      space="local"
      size={0.9}
      onMouseDown={() => {
        if (orbitRef.current) orbitRef.current.enabled = false
      }}
      onMouseUp={() => {
        if (orbitRef.current) orbitRef.current.enabled = true
        onOffsetChange([group.position.x, group.position.y, group.position.z])
        onRotationChange([group.quaternion.x, group.quaternion.y, group.quaternion.z, group.quaternion.w])
      }}
    />
  )
}

interface RobotViewerProps {
  urdfUrl: string
  robotBaseUrl: string
  mountPoints: Record<string, MountPointInfo>
  bodyColors: Record<string, string>
  confirmedPlacements: ConfirmedPlacementView[]
  draftMountPoint: string
  draftUrl: string | null
  offset: Vec3
  rotation: QuaternionXYZW
  onOffsetChange: (offset: Vec3) => void
  onRotationChange: (rotation: QuaternionXYZW) => void
  snapMode: boolean
  transformMode: 'translate' | 'rotate'
}

function RobotScene({
  urdfUrl,
  robotBaseUrl,
  mountPoints,
  bodyColors,
  confirmedPlacements,
  draftMountPoint,
  draftUrl,
  offset,
  rotation,
  onOffsetChange,
  onRotationChange,
  snapMode,
  transformMode,
}: RobotViewerProps) {
  const robot = useURDFRobot(urdfUrl, robotBaseUrl)
  const draftMountInfo = mountPoints[draftMountPoint]
  useBodyColors(robot, bodyColors)
  const orbitRef = useRef<OrbitControlsImpl | null>(null)

  if (!robot) return null

  const handleRobotClick = (event: ThreeEvent<MouseEvent>) => {
    if (!snapMode || !draftMountInfo || !event.face) return
    const link = robot.links[draftMountInfo.link]
    if (!link) return
    event.stopPropagation()

    const worldNormal = event.face.normal.clone().transformDirection(event.object.matrixWorld)
    const localNormal = worldNormal.transformDirection(link.matrixWorld.clone().invert()).normalize()
    const localPoint = link.worldToLocal(event.point.clone())

    const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), localNormal)
    onOffsetChange([localPoint.x, localPoint.y, localPoint.z])
    onRotationChange([quat.x, quat.y, quat.z, quat.w])
  }

  return (
    <>
      <primitive object={robot} onClick={handleRobotClick} />
      {confirmedPlacements.map((p) => (
        <ConfirmedDecoration key={p.key} robot={robot} mountPoints={mountPoints} placement={p} />
      ))}
      <DraftDecoration
        robot={robot}
        mountInfo={draftMountInfo}
        decorationUrl={draftUrl}
        offset={offset}
        rotation={rotation}
        onOffsetChange={onOffsetChange}
        onRotationChange={onRotationChange}
        transformMode={transformMode}
        orbitRef={orbitRef}
      />
      <OrbitControls ref={orbitRef} target={[0, 0.6, 0]} />
    </>
  )
}

export function RobotViewer(props: RobotViewerProps) {
  return (
    <Canvas
      camera={{ position: [1.6, 1.2, 1.6], fov: 50 }}
      style={{ background: '#12151c', cursor: props.snapMode ? 'crosshair' : 'auto' }}
    >
      <ambientLight intensity={0.8} />
      <directionalLight position={[1, 2, 1]} intensity={1.5} />
      <directionalLight position={[-1, 1, -1]} intensity={0.6} />
      <RobotScene {...props} />
      <gridHelper args={[2, 20]} />
    </Canvas>
  )
}
