/* ProMan — nav, dropdowns, before/after sliders */
(function () {
  "use strict";

  /* mobile nav */
  var burger = document.querySelector(".burger");
  var nav = document.getElementById("nav");
  if (burger && nav) {
    burger.addEventListener("click", function () {
      var open = burger.getAttribute("aria-expanded") === "true";
      burger.setAttribute("aria-expanded", String(!open));
      nav.setAttribute("data-open", String(!open));
    });
  }

  /* dropdowns: click on mobile, hover on desktop */
  var mq = window.matchMedia("(min-width: 861px)");
  document.querySelectorAll(".nav__has").forEach(function (item) {
    var btn = item.querySelector("button");
    if (!btn) return;

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = item.getAttribute("data-open") === "true";
      document.querySelectorAll('.nav__has[data-open="true"]').forEach(function (o) {
        if (o !== item) o.setAttribute("data-open", "false");
      });
      item.setAttribute("data-open", String(!open));
    });

    item.addEventListener("mouseenter", function () {
      if (mq.matches) item.setAttribute("data-open", "true");
    });
    item.addEventListener("mouseleave", function () {
      if (mq.matches) item.setAttribute("data-open", "false");
    });
  });

  document.addEventListener("click", function () {
    document.querySelectorAll('.nav__has[data-open="true"]').forEach(function (o) {
      o.setAttribute("data-open", "false");
    });
  });

  /* before / after sliders — a range input drives the clip-path */
  document.querySelectorAll(".ba").forEach(function (ba) {
    var range = ba.querySelector(".ba__range");
    if (!range) return;
    var set = function () {
      ba.style.setProperty("--pos", range.value + "%");
    };
    range.addEventListener("input", set);
    set();
  });

  /* Estimate form. There is no backend to post to, so the details are handed
     to the messaging app instead — every phone has one, and a text reaches a
     contractor faster than email.

     The catch with sms: is that a desktop with nothing registered for it does
     nothing at all, silently, which is indistinguishable from a broken button.
     So the composed message is also written onto the page afterwards, next to
     the number, with a button to copy it. Whatever the device did, the visitor
     ends up holding their message and knowing where to send it. */
  var estimate = document.querySelector("form.form[data-sms]");
  if (estimate) {
    estimate.addEventListener("submit", function (ev) {
      ev.preventDefault();

      var val = function (n) {
        var el = estimate.querySelector('[name="' + n + '"]');
        return el ? el.value.trim() : "";
      };
      var nl = String.fromCharCode(10);

      var lines = ["Estimate request"];
      var add = function (label, v) { if (v) lines.push(label + ": " + v); };
      add("Name", val("name"));
      add("Phone", val("phone"));
      add("Email", val("email"));
      add("Service", val("service"));
      add("Town", val("city"));
      if (val("message")) { lines.push(""); lines.push(val("message")); }
      var text = lines.join(nl);

      /* "?&body=" rather than "?body=" — iOS wanted the ampersand for years
         and both platforms accept this form. */
      var number = estimate.getAttribute("data-sms");
      window.location.href = number + "?&body=" + encodeURIComponent(text);

      var done = estimate.parentNode.querySelector(".sent");
      if (!done) {
        done = document.createElement("div");
        done.className = "sent";
        estimate.parentNode.insertBefore(done, estimate.nextSibling);
      }
      done.innerHTML =
        '<h3>Your message is ready</h3>' +
        '<p>Your texting app should have opened with this in it — press send ' +
        'there and it reaches us. If nothing opened, copy it below and text or ' +
        'call <a href="' + number.replace("sms:", "tel:") + '">' +
        (document.querySelector(".header__phone") ?
          document.querySelector(".header__phone").textContent.trim() :
          number.replace("sms:", "")) + '</a>.</p>' +
        '<pre class="sent__text"></pre>' +
        '<button type="button" class="btn btn--dark sent__copy">Copy the message</button>';
      done.querySelector(".sent__text").textContent = text;

      done.querySelector(".sent__copy").addEventListener("click", function () {
        var btn = this;
        var finish = function (ok) { btn.textContent = ok ? "Copied" : "Select and copy above"; };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () { finish(true); },
                                                   function () { finish(false); });
        } else {
          finish(false);
        }
      });

      done.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }
})();

/* Short clips ---------------------------------------------------------
   The markup ships preload="none", so nothing is fetched until one of
   these scrolls into view. Playback stops again on the way out, which
   keeps a phone from decoding four videos at once.

   Reduced motion is honoured by not autoplaying at all; the clips get
   native controls instead so they are still watchable on request. A
   click toggles playback either way, which is also the pause mechanism
   an auto-playing clip is required to offer. */
(function () {
  "use strict";

  var clips = [].slice.call(document.querySelectorAll(".clip video"));
  if (!clips.length) return;

  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (still || !("IntersectionObserver" in window)) {
    clips.forEach(function (v) { v.setAttribute("controls", ""); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      var v = entry.target;
      if (entry.isIntersecting) {
        if (!v.dataset.held) v.play().catch(function () {});
      } else {
        v.pause();
      }
    });
  }, { threshold: 0.35 });

  clips.forEach(function (v) {
    io.observe(v);
    v.addEventListener("click", function () {
      if (v.paused) { delete v.dataset.held; v.play().catch(function () {}); }
      else { v.dataset.held = "1"; v.pause(); }
    });
  });
})();
