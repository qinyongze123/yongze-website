// B站嵌入视频:滚动到可见区域再加载/播放,不在视野内绝不提前播放。
document.addEventListener("DOMContentLoaded", function () {
  var iframes = document.querySelectorAll("iframe.lazy-bilibili");
  if (!iframes.length) return;

  if (!("IntersectionObserver" in window)) {
    // 不支持就直接全加载,保底
    iframes.forEach(function (iframe) {
      iframe.src = iframe.dataset.src;
    });
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting && !entry.target.src) {
          entry.target.src = entry.target.dataset.src;
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.6 }
  );

  iframes.forEach(function (iframe) {
    observer.observe(iframe);
  });
});
