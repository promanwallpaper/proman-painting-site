/* ProMan — pointer and scroll micro-interactions.
 *
 * Deliberately not a module and with no dependency on Three.js: these effects
 * are cheap and should run everywhere the WebGL background does not, which is
 * most phones. Everything here is off when the visitor asked for reduced
 * motion, and the pointer effects additionally require a real pointer, so a
 * touch device never pays for hover logic it cannot trigger.
 *
 * All work happens inside one requestAnimationFrame loop that only runs while
 * something is actually animating.
 */
(function () {
  "use strict";

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* one shared loop -------------------------------------------------- */

  var jobs = [];
  var running = false;

  function loop() {
    var alive = false;
    for (var i = 0; i < jobs.length; i++) {
      if (jobs[i]()) alive = true;
    }
    if (alive) requestAnimationFrame(loop);
    else running = false;
  }

  function wake() {
    if (running) return;
    running = true;
    requestAnimationFrame(loop);
  }

  /* magnetic buttons -------------------------------------------------
   * The button leans toward the cursor while it is nearby and springs back
   * when it leaves. Strength is capped so the hit area never runs away from
   * the pointer. */

  function magnetic(el) {
    var tx = 0, ty = 0, cx = 0, cy = 0, active = false;
    var PULL = 0.28, MAX = 9;

    el.addEventListener("pointermove", function (e) {
      var r = el.getBoundingClientRect();
      var dx = e.clientX - (r.left + r.width / 2);
      var dy = e.clientY - (r.top + r.height / 2);
      tx = Math.max(-MAX, Math.min(MAX, dx * PULL));
      ty = Math.max(-MAX, Math.min(MAX, dy * PULL));
      active = true;
      wake();
    });

    el.addEventListener("pointerleave", function () {
      tx = 0; ty = 0;
      active = true;
      wake();
    });

    jobs.push(function () {
      if (!active) return false;
      cx += (tx - cx) * 0.18;
      cy += (ty - cy) * 0.18;
      if (Math.abs(cx - tx) < 0.05 && Math.abs(cy - ty) < 0.05) {
        cx = tx; cy = ty;
        active = false;
      }
      el.style.transform = "translate3d(" + cx.toFixed(2) + "px," + cy.toFixed(2) + "px,0)";
      return active;
    });
  }

  /* card tilt --------------------------------------------------------
   * Rotation is tiny on purpose — enough to read as depth on a photo card,
   * not enough to make body text inside it wobble. */

  function tilt(el) {
    var rx = 0, ry = 0, crx = 0, cry = 0, active = false;
    var MAX = 4.5;

    el.addEventListener("pointermove", function (e) {
      var r = el.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width - 0.5;
      var py = (e.clientY - r.top) / r.height - 0.5;
      ry = px * MAX * 2;
      rx = -py * MAX * 2;
      active = true;
      wake();
    });

    el.addEventListener("pointerleave", function () {
      rx = 0; ry = 0;
      active = true;
      wake();
    });

    jobs.push(function () {
      if (!active) return false;
      crx += (rx - crx) * 0.14;
      cry += (ry - cry) * 0.14;
      if (Math.abs(crx - rx) < 0.02 && Math.abs(cry - ry) < 0.02) {
        crx = rx; cry = ry;
        active = false;
      }
      el.style.transform =
        "perspective(900px) rotateX(" + crx.toFixed(2) + "deg) rotateY(" +
        cry.toFixed(2) + "deg)";
      return active;
    });
  }

  if (finePointer) {
    document.querySelectorAll(".btn").forEach(magnetic);
    document.querySelectorAll(".card, .feature__media").forEach(tilt);
  }

  /* parallax ---------------------------------------------------------
   * Anything carrying data-parallax="0.15" drifts at that fraction of the
   * scroll distance, measured from where it sits in the viewport. */

  var layers = [].slice.call(document.querySelectorAll("[data-parallax]"));

  /* scroll velocity --------------------------------------------------
   * Exposed as --scroll-velocity on <html> (0..1) so stylesheets can react
   * without touching JS, and used here to shear the parallax layers very
   * slightly in the direction of travel. */

  var lastY = window.scrollY;
  var vel = 0, smoothVel = 0;
  var root = document.documentElement;

  function onScroll() {
    var y = window.scrollY;
    vel = y - lastY;
    lastY = y;
    wake();
  }

  if (layers.length || true) {
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  jobs.push(function () {
    smoothVel += (vel - smoothVel) * 0.12;
    vel *= 0.82;

    var norm = Math.min(Math.abs(smoothVel) / 45, 1);
    root.style.setProperty("--scroll-velocity", norm.toFixed(3));

    var vh = window.innerHeight;
    for (var i = 0; i < layers.length; i++) {
      var el = layers[i];
      var rate = parseFloat(el.dataset.parallax) || 0.1;
      var r = el.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) continue;
      var offset = (r.top + r.height / 2 - vh / 2) * -rate;
      el.style.transform =
        "translate3d(0," + offset.toFixed(1) + "px,0) skewY(" +
        (smoothVel * 0.012).toFixed(3) + "deg)";
    }

    // keep spinning while there is still momentum to bleed off
    return Math.abs(smoothVel) > 0.05;
  });

  wake();
})();
