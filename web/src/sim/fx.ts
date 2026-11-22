// Particle effects for Live scenes: spark bursts (fireworks), spinning wheels (girandole), smoke puffs that grow to a
// capped size and fade, fireballs with a flash (explosions). Pools are fixed; everything stops on its own.
import * as THREE from 'three/webgpu';

const R = Math.random;
interface Spark { p: THREE.Vector3; v: THREE.Vector3; life: number; c: THREE.Color }
interface Puff { m: THREE.Mesh; age: number; life: number; max: number; rise: number; y0: number }
interface Ball { m: THREE.Mesh; age: number; life: number; max: number }
interface Wheel { at: THREE.Vector3; axis: THREE.Vector3; age: number; life: number; acc: number }

export function createFX(root: THREE.Object3D, N = 1600) {
  const sparkGeo = new THREE.IcosahedronGeometry(0.1, 0);
  const sparkMesh = new THREE.InstancedMesh(sparkGeo, new THREE.MeshBasicMaterial({ color: 0xffffff, toneMapped: false }), N);
  sparkMesh.count = 0; sparkMesh.frustumCulled = false; root.add(sparkMesh);
  const sparks: Spark[] = [], puffs: Puff[] = [], balls: Ball[] = [], wheels: Wheel[] = [];
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3();
  const light = new THREE.PointLight(0xffb060, 0, 160, 1.6); root.add(light);
  let flash = 0;

  function spark(p: THREE.Vector3, v: THREE.Vector3, life: number, c: THREE.Color) {
    if (sparks.length >= N) sparks.shift();
    sparks.push({ p: p.clone(), v, life, c });
  }
  /** Fireworks burst: a sphere of sparks in one or two colours. */
  function burst(at: THREE.Vector3, n = 90, speed = 9, colors = [0xffd27a, 0xff6a3a, 0xfff4d0], life = 1.6) {
    for (let i = 0; i < n; i++) {
      const d = new THREE.Vector3(R() - 0.5, R() - 0.3, R() - 0.5).normalize().multiplyScalar(speed * (0.6 + R() * 0.4));
      spark(at, d, life * (0.7 + R() * 0.5), new THREE.Color(colors[(R() * colors.length) | 0]));
    }
  }
  /** Spinning wheel firework (girandola): sparks thrown off tangentially for `life` seconds. */
  function wheel(at: THREE.Vector3, axis = new THREE.Vector3(1, 0, 0), life = 6) { wheels.push({ at: at.clone(), axis: axis.clone().normalize(), age: 0, life, acc: 0 }); }
  /** Smoke puff: grows to `max` metres, rises at most `rise` metres, fades out over `life` seconds. */
  const smokeMat = new THREE.MeshStandardMaterial({ color: 0xcfc8bc, transparent: true, opacity: 0.7, depthWrite: false, roughness: 1 });
  function puff(at: THREE.Vector3, max = 3, life = 10, rise = 6, color?: number) {
    const m = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 1), smokeMat.clone()); if (color !== undefined) (m.material as any).color.set(color);
    m.position.copy(at); m.scale.setScalar(max * 0.3); root.add(m); puffs.push({ m, age: 0, life, max, rise, y0: at.y });
  }
  /** Explosion: flash, fireball, debris sparks, dark smoke column (capped). */
  function explode(at: THREE.Vector3, size = 1) {
    const m = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 2), new THREE.MeshBasicMaterial({ color: 0xffa040, transparent: true, opacity: 0.95, toneMapped: false }));
    m.position.copy(at); m.scale.setScalar(0.5); root.add(m); balls.push({ m, age: 0, life: 1.4, max: 9 * size });
    burst(at, 140, 22 * size, [0xffc060, 0x8a6a4a, 0x5a4a3a], 2.2);
    for (let i = 0; i < 6; i++) puff(at.clone().add(new THREE.Vector3((R() - 0.5) * 6, i * 2.2, (R() - 0.5) * 6)), 7 * size, 22, 14, 0x4a4540);
    light.position.copy(at).setY(at.y + 6); flash = 1;
  }
  function update(dt: number) {
    for (const w of wheels) {                     // emit from the rim of the turning wheel
      w.age += dt; w.acc += dt * 60; if (w.age > w.life) continue;
      const ang = w.age * 14, side = new THREE.Vector3(0, 1, 0).applyAxisAngle(w.axis, ang).multiplyScalar(0.8);
      while (w.acc > 1) { w.acc--; const tg = side.clone().cross(w.axis).normalize().multiplyScalar(7);
        spark(w.at.clone().add(side), tg.add(new THREE.Vector3(0, 1.5, 0)), 0.7, new THREE.Color(R() < 0.5 ? 0xffe08a : 0xffffff)); }
    }
    for (let i = wheels.length - 1; i >= 0; i--) if (wheels[i].age > wheels[i].life) wheels.splice(i, 1);
    let k = 0;
    for (let i = sparks.length - 1; i >= 0; i--) {
      const s = sparks[i]; s.life -= dt; if (s.life <= 0) { sparks.splice(i, 1); continue; }
      s.v.y -= 9.8 * dt; s.v.multiplyScalar(1 - 0.9 * dt); s.p.addScaledVector(s.v, dt);
      m4.compose(s.p, q, sc.setScalar(Math.min(1, s.life * 2))); sparkMesh.setMatrixAt(k, m4); sparkMesh.setColorAt(k, s.c); k++;
    }
    sparkMesh.count = k; sparkMesh.instanceMatrix.needsUpdate = true; if (sparkMesh.instanceColor) sparkMesh.instanceColor.needsUpdate = true;
    for (let i = puffs.length - 1; i >= 0; i--) {
      const p = puffs[i]; p.age += dt; const f = p.age / p.life;
      if (f >= 1) { root.remove(p.m); p.m.geometry.dispose(); puffs.splice(i, 1); continue; }
      p.m.scale.setScalar(p.max * (0.3 + 0.7 * Math.min(1, f * 2.5)));          // grows quickly, then stops growing
      if (p.m.position.y - p.y0 < p.rise) p.m.position.y += dt * p.rise / p.life * 1.5;
      (p.m.material as any).opacity = 0.7 * (1 - f) * (1 - f);
    }
    for (let i = balls.length - 1; i >= 0; i--) {
      const b = balls[i]; b.age += dt; const f = b.age / b.life;
      if (f >= 1) { root.remove(b.m); balls.splice(i, 1); continue; }
      b.m.scale.setScalar(b.max * Math.sqrt(f)); (b.m.material as any).opacity = 0.95 * (1 - f);
    }
    flash = Math.max(0, flash - dt * 1.5); light.intensity = flash * 6000;
  }
  function clear() {
    sparks.length = 0; wheels.length = 0; sparkMesh.count = 0;
    for (const p of puffs) root.remove(p.m); puffs.length = 0; for (const b of balls) root.remove(b.m); balls.length = 0; flash = 0; light.intensity = 0;
  }
  return { burst, wheel, puff, explode, update, clear };
}
export type FX = ReturnType<typeof createFX>;
