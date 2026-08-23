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

  /* estimate form with no backend yet — a mailto: POST goes nowhere in most
     browsers, so build the mailto: link ourselves and let the mail app open */
  var estimate = document.querySelector("form.form[data-mailto]");
  if (estimate) {
    estimate.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var val = function (n) {
        var el = estimate.querySelector('[name="' + n + '"]');
        return el ? el.value.trim() : "";
      };
      var body = [
        "Name: " + val("name"),
        "Phone: " + val("phone"),
        "Email: " + val("email"),
        "Service: " + val("service"),
        "Town: " + val("city"),
        "",
        val("message")
      ].join(String.fromCharCode(10));
      var subject = "Estimate request" + (val("service") ? " — " + val("service") : "");
      window.location.href = "mailto:" + estimate.getAttribute("data-mailto") +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(body);
    });
  }
})();
