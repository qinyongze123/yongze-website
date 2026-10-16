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


// 侧边目录(.toc-side,见 build.py 的 {{toc}} 和 style.css 的"目录"一节):
// 显示与否由 CSS 媒体查询决定(宽屏显示侧边、隐藏正文里的那份);这里只做两件事:
// - 按文章实际位置把它贴在文章右侧 40px 处;
// - 随滚动高亮当前小节:最后一个顶边已经过了视口 130px 位置的 h2;还没读到第一节时不高亮。
(function () {
  var side = document.querySelector(".toc-side");
  var article = document.querySelector(".article-body");
  if (!side || !article) return;
  var heads = [];
  side.querySelectorAll("a").forEach(function (a) {
    var h = document.getElementById(a.getAttribute("href").slice(1));
    if (h) heads.push({ link: a, el: h });
  });

  function place() {
    var left = article.getBoundingClientRect().right + 40;
    side.style.left = left + "px";
    side.style.width = Math.max(140, Math.min(200, window.innerWidth - left - 16)) + "px";
  }

  var ticking = false;
  function update() {
    ticking = false;
    var current = null;
    heads.forEach(function (h) {
      if (h.el.getBoundingClientRect().top <= 130) current = h;
    });
    heads.forEach(function (h) {
      h.link.classList.toggle("is-active", h === current);
    });
  }
  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", function () { place(); onScroll(); });
  window.addEventListener("load", function () { place(); onScroll(); });
  place();
  update();
})();
