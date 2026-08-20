/* ProMan — WebGL background.
 *
 * 6500 points that morph between three formations as the page scrolls:
 * a wave across the top of the page, a stream through the middle, a lattice
 * at the bottom. Behind them sits a slow gradient shader in the brand
 * graphite, lit with the brand orange.
 *
 * The whole thing is optional. It refuses to start on small screens, when the
 * visitor asked for reduced motion, and when WebGL is missing — the hero keeps
 * its flat graphite background in that case and nothing is downloaded twice.
 */

import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const COUNT = 6500;
const MIN_WIDTH = 900;          // below this the scene is not worth the battery
const MAX_PIXEL_RATIO = 1.5;    // retina at 2x doubles the fragment cost for little gain

const INK = new THREE.Color('#2b2b2b');
const ORANGE = new THREE.Color('#e8792b');

/* ---------------------------------------------------------------- guards */

function supported() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
  if (window.innerWidth < MIN_WIDTH) return false;
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext &&
              (c.getContext('webgl2') || c.getContext('webgl')));
  } catch (err) {
    return false;
  }
}

/* ------------------------------------------------------------ formations */

/* Each formation fills one Float32Array of xyz triples. They are built once
 * and handed to the GPU as three attributes; the vertex shader mixes between
 * them, so morphing costs nothing on the CPU. */

function wave(i, n, out, o) {
  const cols = Math.ceil(Math.sqrt(n));
  const x = (i % cols) / cols - 0.5;
  const z = Math.floor(i / cols) / cols - 0.5;
  out[o] = x * 26;
  out[o + 1] = Math.sin(x * 9) * Math.cos(z * 7) * 1.7 - 1.5;
  out[o + 2] = z * 26;
}

function stream(i, n, out, o) {
  const t = i / n;
  const angle = t * Math.PI * 22;
  const radius = 1.1 + Math.sin(t * Math.PI * 4) * 0.85;
  out[o] = (t - 0.5) * 34;
  out[o + 1] = Math.sin(angle) * radius;
  out[o + 2] = Math.cos(angle) * radius;
}

function lattice(i, n, out, o) {
  const side = Math.ceil(Math.cbrt(n));
  const x = i % side;
  const y = Math.floor(i / side) % side;
  const z = Math.floor(i / (side * side));
  const step = 1.5;
  const half = (side - 1) * step * 0.5;
  out[o] = x * step - half;
  out[o + 1] = y * step - half;
  out[o + 2] = z * step - half;
}

function formation(fn) {
  const arr = new Float32Array(COUNT * 3);
  for (let i = 0; i < COUNT; i++) fn(i, COUNT, arr, i * 3);
  return new THREE.BufferAttribute(arr, 3);
}

/* --------------------------------------------------------------- shaders */

const POINT_VERT = `
uniform float uProgress;   // 0 = wave, 1 = stream, 2 = lattice
uniform float uTime;
uniform float uSize;
uniform float uPixelRatio;

attribute vec3 posWave;
attribute vec3 posStream;
attribute vec3 posGrid;
attribute float aSeed;

varying float vGlow;

void main() {
  // uProgress walks 0..2; mix the two formations either side of it.
  vec3 a = uProgress < 1.0 ? posWave  : posStream;
  vec3 b = uProgress < 1.0 ? posStream : posGrid;
  float t = uProgress < 1.0 ? uProgress : uProgress - 1.0;
  t = smoothstep(0.0, 1.0, t);
  vec3 pos = mix(a, b, t);

  // a little independent drift so the formations never look frozen
  float drift = uTime * 0.35 + aSeed * 6.2831;
  pos.x += sin(drift) * 0.16;
  pos.y += cos(drift * 0.9) * 0.16;

  vec4 mv = modelViewMatrix * vec4(pos, 1.0);
  gl_Position = projectionMatrix * mv;

  // brighter where the point sits near the axis of the stream
  vGlow = clamp(1.0 - length(pos.yz) * 0.18, 0.0, 1.0) * (0.45 + aSeed * 0.55);

  gl_PointSize = uSize * uPixelRatio * (14.0 / -mv.z);
}
`;

const POINT_FRAG = `
uniform vec3 uInk;
uniform vec3 uOrange;

varying float vGlow;

void main() {
  // round, soft-edged point
  vec2 d = gl_PointCoord - 0.5;
  float r = dot(d, d);
  if (r > 0.25) discard;
  float alpha = smoothstep(0.25, 0.02, r);

  vec3 col = mix(uInk * 2.6, uOrange, vGlow);
  gl_FragColor = vec4(col, alpha * (0.30 + vGlow * 0.7));
}
`;

const BG_VERT = `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position.xy, 0.0, 1.0);
}
`;

const BG_FRAG = `
uniform float uTime;
uniform vec2 uResolution;
uniform vec3 uInk;
uniform vec3 uOrange;

varying vec2 vUv;

// cheap value noise — two octaves is plenty for a slow gradient
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1, 0)), u.x),
             mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), u.x), u.y);
}

void main() {
  vec2 uv = vUv;
  vec2 p = uv * vec2(uResolution.x / uResolution.y, 1.0);

  float n = noise(p * 2.4 + uTime * 0.03) * 0.6
          + noise(p * 5.1 - uTime * 0.02) * 0.4;

  // vignette keeps the edges dark so page text stays readable over it
  float vign = smoothstep(1.15, 0.25, length(uv - 0.5) * 1.4);

  vec3 col = uInk * (0.55 + n * 0.5);
  col += uOrange * pow(n, 3.0) * 0.5 * vign;

  gl_FragColor = vec4(col, 1.0);
}
`;

/* ------------------------------------------------------------------ main */

function start(canvas) {
  const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: false,          // bloom hides the aliasing; MSAA is not worth it here
    powerPreference: 'high-performance',
    alpha: false,
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO));
  renderer.setSize(window.innerWidth, window.innerHeight, false);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    55, window.innerWidth / window.innerHeight, 0.1, 120);
  camera.position.set(0, 0, 17);

  /* background quad — drawn first, never depth-tested */
  const bgUniforms = {
    uTime: { value: 0 },
    uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
    uInk: { value: INK },
    uOrange: { value: ORANGE },
  };
  const bg = new THREE.Mesh(
    new THREE.PlaneGeometry(2, 2),
    new THREE.ShaderMaterial({
      vertexShader: BG_VERT,
      fragmentShader: BG_FRAG,
      uniforms: bgUniforms,
      depthWrite: false,
      depthTest: false,
    }));
  bg.frustumCulled = false;
  bg.renderOrder = -1;
  scene.add(bg);

  /* points */
  const geo = new THREE.BufferGeometry();
  const posWave = formation(wave);
  geo.setAttribute('position', posWave.clone());   // needed for bounds
  geo.setAttribute('posWave', posWave);
  geo.setAttribute('posStream', formation(stream));
  geo.setAttribute('posGrid', formation(lattice));

  const seeds = new Float32Array(COUNT);
  for (let i = 0; i < COUNT; i++) seeds[i] = Math.random();
  geo.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1));
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 40);

  const pointUniforms = {
    uProgress: { value: 0 },
    uTime: { value: 0 },
    uSize: { value: 2.4 },
    uPixelRatio: { value: renderer.getPixelRatio() },
    uInk: { value: INK },
    uOrange: { value: ORANGE },
  };
  const points = new THREE.Points(geo, new THREE.ShaderMaterial({
    vertexShader: POINT_VERT,
    fragmentShader: POINT_FRAG,
    uniforms: pointUniforms,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  }));
  points.frustumCulled = false;
  scene.add(points);

  /* postprocessing */
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.62,   // strength
    0.85,   // radius
    0.22);  // threshold
  composer.addPass(bloom);
  composer.addPass(new OutputPass());
  composer.setSize(window.innerWidth, window.innerHeight);

  /* ---- scroll drives the morph, eased so it never snaps ---- */
  let target = 0;
  let current = 0;

  function readScroll() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const p = max > 0 ? window.scrollY / max : 0;
    target = Math.min(Math.max(p, 0), 1) * 2;   // 0..2 across the three states
  }
  readScroll();
  window.addEventListener('scroll', readScroll, { passive: true });

  /* ---- resize ---- */
  let resizeTimer = 0;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      const w = window.innerWidth, h = window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h, false);
      composer.setSize(w, h);
      bloom.setSize(w, h);
      bgUniforms.uResolution.value.set(w, h);
      pointUniforms.uPixelRatio.value = renderer.getPixelRatio();
    }, 150);
  }, { passive: true });

  /* ---- loop, paused whenever the tab is not being looked at ---- */
  /* Own clock rather than THREE.Clock, which r185 deprecates, and with a
   * clamped delta so coming back to a backgrounded tab resumes where the
   * animation left off instead of jumping forward by the time spent away. */
  let elapsed = 0;
  let last = performance.now();
  let running = !document.hidden;
  let frame = 0;

  document.addEventListener('visibilitychange', function () {
    running = !document.hidden;
    if (running) { last = performance.now(); tick(); }
    else cancelAnimationFrame(frame);
  });

  function tick() {
    if (!running) return;
    frame = requestAnimationFrame(tick);

    const now = performance.now();
    elapsed += Math.min((now - last) / 1000, 0.1);
    last = now;
    const t = elapsed;
    current += (target - current) * 0.06;

    bgUniforms.uTime.value = t;
    pointUniforms.uTime.value = t;
    pointUniforms.uProgress.value = current;

    // the whole field turns slowly; enough to read as depth, not enough to distract
    points.rotation.y = t * 0.045 + current * 0.5;
    points.rotation.x = Math.sin(t * 0.09) * 0.09;

    composer.render();
  }

  // Only now does the stylesheet let the hero and footer go transparent. If we
  // never get here — no WebGL, small screen, reduced motion — they keep their
  // flat brand backgrounds and the page looks exactly as it did before.
  document.documentElement.dataset.scene = 'on';
  tick();
}

/* --------------------------------------------------------------- kickoff */

const canvas = document.getElementById('bg-canvas');

if (canvas && supported()) {
  // Wait for first paint so the scene never competes with the LCP image.
  if (document.readyState === 'complete') start(canvas);
  else window.addEventListener('load', function () { start(canvas); }, { once: true });
} else if (canvas) {
  canvas.remove();
}
