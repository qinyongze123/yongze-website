// 文章页顶部的阅读进度条。元素是这里动态创建的(没有写进 build.py 的模板),
// 不是文章页(页面里没有 .article-body)就什么都不做。
(function () {
  if (!document.querySelector(".article-body")) return;

  var bar = document.createElement("div");
  bar.className = "read-progress";
  bar.setAttribute("aria-hidden", "true");
  var fill = document.createElement("i");
  bar.appendChild(fill);
  document.body.appendChild(bar);

  var ticking = false;
  function update() {
    ticking = false;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    fill.style.transform = "scaleX(" + p + ")";
  }
  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  window.addEventListener("load", onScroll); // 图片加载完页面变长了,重新算一次
  update();
})();

// 语言开关(侧边栏"语言 [中文|EN]"):点击时滑块先滑到另一边,稍等一下再跳转到
// 另一种语言的对应页面。按住 Ctrl/Cmd/Shift、中键(新标签页打开)、或系统开了
// "减少动态效果"时不拦截,走浏览器默认的链接行为。
(function () {
  var toggle = document.querySelector(".lang-toggle");
  if (!toggle) return;

  var checked = toggle.getAttribute("aria-checked");
  toggle.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    e.preventDefault();
    toggle.classList.add("is-flipping");
    toggle.setAttribute("aria-checked", checked === "true" ? "false" : "true");
    var href = toggle.href;
    setTimeout(function () { window.location.href = href; }, 280);
  });

  // 点了开关后按浏览器"后退"回来,页面可能是从缓存里原样恢复的(滑块还停在翻过去的位置),这里复位
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      toggle.classList.remove("is-flipping");
      toggle.setAttribute("aria-checked", checked);
    }
  });
})();
